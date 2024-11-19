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
    """
    Удаление старых записей задач APScheduler из базы данных.
    :param max_age: Максимальный возраст записей в секундах. По умолчанию: 7 дней.
    """
    threshold = timezone.now() - timedelta(seconds=max_age)
    DjangoJobExecution.objects.filter(run_time__lte=threshold).delete()
    logger.info(f"Старые записи задач (старше {max_age} секунд) успешно удалены.")


class SendMail:
    def __init__(self):
        logger.info("Инициализация класса SendMail")

    def get_mailings(self):
        """Получение рассылок для обработки."""
        mailings = Mailing.objects.filter(
            status=Mailing.Status.CREATED, datetime_first_mailing__lte=timezone.now()
        )
        for mailing in mailings:
            mailing.status = Mailing.Status.STARTED
            mailing.save()
            logger.info(f"Статус рассылки {mailing.id} изменен на 'STARTED'")
        return mailings

    def send_mailing(self):
        """Отправка рассылки клиентам."""
        mailings = Mailing.objects.filter(status=Mailing.Status.STARTED)
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

    def finished_status(self):
        """Завершение рассылок, если все письма обработаны."""
        mailings_f = Mailing.objects.filter(status=Mailing.Status.STARTED)
        logger.info("Обработка завершенных рассылок")
        for mailing in mailings_f:
            if mailing.status == Mailing.Status.STARTED:
                mailing.status = Mailing.Status.FINISHED
                mailing.save()
                logger.info(f"Статус рассылки {mailing.id} изменен на 'FINISHED'")

    def get_cron_trigger(self, mailing):
        """Получение расписания для выполнения рассылки."""
        if mailing.frequency == Mailing.Frequency.DAY:
            # return CronTrigger(hour=0, minute=0)  # Ежедневно в полночь
            return CronTrigger(minute="1")
        elif mailing.frequency == Mailing.Frequency.WEEK:
            return CronTrigger(
                day_of_week="mon", hour=0, minute=0
            )  # Еженедельно в понедельник
        elif mailing.frequency == Mailing.Frequency.MONTH:
            return CronTrigger(
                day=1, hour=0, minute=0
            )  # Ежемесячно в первый день месяца
        else:
            logger.error(
                f"[Рассылка ID {mailing.id}] Неизвестная частота: {mailing.frequency}"
            )
            return None


class Command(BaseCommand):
    help = "Запуск планировщика рассылок APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        send_mail_service = SendMail()
        mailings = send_mail_service.get_mailings()

        for mailing in mailings:
            cron_trigger = send_mail_service.get_cron_trigger(mailing)
            if cron_trigger:
                scheduler.add_job(
                    send_mail_service.send_mailing,
                    trigger=cron_trigger,
                    id=f"send_mailing_{mailing.id}",
                    max_instances=1,
                    misfire_grace_time=60,  # 60 секунд для обработки пропущенной задачи
                    replace_existing=True,
                )
                logger.info(f"Добавлена задача для рассылки {mailing.id}.")

        # Задача для удаления старых записей
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'delete_old_job_executions'.")

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            send_mail_service.finished_status()
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")

    SendMail().finished_status()
