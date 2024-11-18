import logging
from datetime import datetime

from django.core.mail import send_mail
from django.utils import timezone
import pytz
from newsletter.models import Mailing, MailingAttempt

import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)



@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class SendMail:
    def __init__(self):
        logger.info("Инициализация класса SendMail")

    def get_mailings(self):
        # Получить актуальные рассылки
        zone = timezone.get_current_timezone()
        current_datetime = datetime.now(zone)
        return Mailing.objects.filter(
            datetime_first_mailing__lte=current_datetime,
            status=Mailing.Status.CREATED,
        )

    def send_mailing(self):
        mailings = self.get_mailings()

        for mailing in mailings:
            try:
                subject = mailing.message.subject
                content = mailing.message.content
                recipients = [client.email for client in mailing.clients.all()]

                logger.info(f"Отправка рассылки {mailing.id} клиентам: {recipients}")
                send_mail(
                    subject=subject,
                    message=content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=recipients,
                )

                mailing.status = Mailing.Status.STARTED
                mailing.save()

                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение отправлено успешно",
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

    def get_cron_trigger(self, mailing):
        # Создать крон-триггер для конкретной рассылки
        if mailing.frequency == Mailing.Frequency.DAY:
            return CronTrigger(day=1)
        elif mailing.frequency == Mailing.Frequency.WEEK:
            return CronTrigger(week=1)
        elif mailing.frequency == Mailing.Frequency.MONTH:
            return CronTrigger(month=1)
        else:
            logger.error(f"Неизвестная частота рассылки: {mailing.frequency}")
            return None


class Command(BaseCommand):
    help = "Runs APScheduler."

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
                    replace_existing=True,
                )
                logger.info(f"Добавлена задача для рассылки {mailing.id}.")

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
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")
