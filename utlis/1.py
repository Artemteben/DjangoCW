import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from newsletter.models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def send_mailing():
    """
    Функция для отправки рассылки.
    """
    logger.info("Запуск функции send_mailing.")
    current_datetime = timezone.now()
    mailings = Mailing.objects.filter(
        datetime_first_mailing__lte=current_datetime,
        status=Mailing.Status.CREATED,
    )

    for mailing in mailings:
        logger.info(f"Обработка рассылки {mailing.id}.")
        try:
            subject = mailing.message.subject
            content = mailing.message.content
            recipients = [client.email for client in mailing.clients.all()]

            logger.info(f"Отправка рассылки {mailing.id} клиентам: {recipients}.")
            send_mail(
                subject=subject,
                message=content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipients,
            )

            # Обновление статуса и добавление успешной попытки
            mailing.status = Mailing.Status.STARTED
            mailing.save()
            MailingAttempt.objects.create(
                mailing=mailing,
                datetime_attempt=timezone.now(),
                status=MailingAttempt.Status.SUCCESS,
                server_response="Сообщение отправлено успешно.",
            )
            logger.info(f"Рассылка {mailing.id} отправлена успешно.")
        except Exception as e:
            logger.error(f"Ошибка отправки рассылки {mailing.id}: {e}")
            MailingAttempt.objects.create(
                mailing=mailing,
                datetime_attempt=timezone.now(),
                status=MailingAttempt.Status.FAILED,
                server_response=str(e),
            )


def delete_old_job_executions(max_age=604_800):
    """
    Удаляет записи о выполнении задач старше `max_age`.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Управление рассылками с использованием APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_mailing,
            trigger=CronTrigger(minute="*/10"),  # Каждые 10 минут
            id="send_mailing",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'send_mailing'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена еженедельная задача 'delete_old_job_executions'.")

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен.")
