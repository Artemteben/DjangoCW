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
        zone = timezone.get_current_timezone()
        current_datetime = datetime.now(zone)
        mailings = Mailing.objects.filter(
            status=Mailing.Status.CREATED,
        )
        for mailing in mailings:
            mailing.status = Mailing.Status.STARTED
            mailing.save()
            logger.info(f"Статус рассылки {mailing.id} изменен на 'STARTED'")
        return mailings

    def send_mailing(self):
        mailings = self.get_mailings()
        for mailing in mailings:
            success_count, fail_count = 0, 0
            try:
                subject = mailing.message.subject
                content = mailing.message.content
                recipients = mailing.clients.values_list("email", flat=True)
                logger.info(
                    f"[Рассылка ID {mailing.id}] Отправка клиентам: {list(recipients)}"
                )

                send_mail(
                    subject=subject,
                    message=content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=list(recipients),
                )

                success_count += len(recipients)
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение отправлено успешно",
                )
            except Exception as e:
                fail_count += 1
                logger.error(f"[Рассылка ID {mailing.id}] Ошибка: {e}")
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.FAILED,
                    server_response=str(e),
                )
            logger.info(
                f"[Рассылка ID {mailing.id}] Успешно отправлено: {success_count}, Ошибки: {fail_count}"
            )

    def get_cron_trigger(self, mailing):
        if mailing.frequency == Mailing.Frequency.DAY:
            # return CronTrigger(hour=0, minute=0)
            return CronTrigger(minute="1")
        elif mailing.frequency == Mailing.Frequency.WEEK:
            return CronTrigger(day_of_week="mon", hour=0, minute=0)
        elif mailing.frequency == Mailing.Frequency.MONTH:
            return CronTrigger(day=1, hour=0, minute=0)
        else:
            logger.error(
                f"[Рассылка ID {mailing.id}] Неизвестная частота: {mailing.frequency}"
            )
            return CronTrigger(minute=1)

    # datetime_first_mailing__lte = current_datetime

    def finished_status(self):
        mailings = self.get_mailings()
        for mailing in mailings:
            if mailing.status == Mailing.Status.STARTED:
                mailing.status = Mailing.Status.FINISHED
                mailing.save()
                logger.info(f"Статус рассылки {mailing.id} изменен на 'FINISHED'")


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

        # scheduler.add_job(
        #     delete_old_job_executions,
        #     trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        #     id="delete_old_job_executions",
        #     max_instances=1,
        #     replace_existing=True,
        # )
        # logger.info("Добавлена задача 'delete_old_job_executions'.")

        try:
            logger.info("Запуск планировщика...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("finished_status")
            send_mail_service.finished_status()
            logger.info("Остановка планировщика...")
            scheduler.shutdown()
            logger.info("Планировщик успешно остановлен!")
