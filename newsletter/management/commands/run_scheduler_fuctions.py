import inspect
import logging
from datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from newsletter.models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """Удаление старых записей задач APScheduler из базы данных."""
    threshold = timezone.now() - timedelta(seconds=max_age)
    DjangoJobExecution.objects.filter(run_time__lte=threshold).delete()
    logger.info(f"Старые записи задач (старше {max_age} секунд) успешно удалены.")


def get_mailing_list():
    """Получение всех активных рассылок для обработки."""
    now = timezone.now()
    return Mailing.objects.filter(
        datetime_first_mailing__lte=now,
        date_time_last_mailing__gte=now,
    )


def update_mailing_status():
    """Обновление статусов рассылок."""
    mailings = get_mailing_list()
    for mailing in mailings:
        if mailing.status == Mailing.Status.CREATED:
            mailing.status = Mailing.Status.STARTED
            mailing.save()
            logger.info(f"Статус рассылки {mailing.id} изменен на 'STARTED'")
        elif (
            mailing.status == Mailing.Status.STARTED
            and mailing.date_time_last_mailing < timezone.now()
        ):
            mailing.status = Mailing.Status.FINISHED
            mailing.save()
            logger.info(f"Статус рассылки {mailing.id} изменен на 'FINISHED'")


def get_cron_trigger(mailing):
    """Получение расписания для выполнения рассылки."""
    if mailing.frequency == Mailing.Frequency.DAY:
        return CronTrigger(hour=0, minute=0)
    elif mailing.frequency == Mailing.Frequency.WEEK:
        return CronTrigger(day_of_week="mon", hour=0, minute=0)
    elif mailing.frequency == Mailing.Frequency.MONTH:
        return CronTrigger(day=1, hour=0, minute=0)
    else:
        logger.error(
            f"[Рассылка ID {mailing.id}] Неизвестная частота: {mailing.frequency}"
        )
        return None


def send_mailing():
    """Отправка рассылки клиентам."""
    mailings = get_mailing_list()
    for mailing in mailings:
        success_count, fail_count = 0, 0
        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                )
                success_count += 1
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение отправлено успешно",
                )
            except Exception as e:
                fail_count += 1
                logger.error(
                    f"[Рассылка ID {mailing.id}] Ошибка для клиента {client.email}: {e}"
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.FAILED,
                    server_response=str(e),
                )

        logger.info(
            f"[Рассылка ID {mailing.id}] Успешно отправлено: {success_count}, Ошибки: {fail_count}"
        )


class Command(BaseCommand):
    help = "Запуск планировщика рассылок APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Обновление статусов рассылок
        scheduler.add_job(
            update_mailing_status,
            trigger=CronTrigger(minute="*/5"),  # Каждые 5 минут
            id="update_mailing_status",
            replace_existing=True,
        )

        # Отправка рассылок
        scheduler.add_job(
            send_mailing,
            trigger=CronTrigger(minute="*/10"),  # Каждые 10 минут
            id="send_mailing",
            replace_existing=True,
        )

        # Удаление старых записей
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            replace_existing=True,
        )

        logger.info("Запуск планировщика...")
        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")
