import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from newsletter.models import Mailing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Отправка рассылок"

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

    def handle(self, *args, **kwargs):

        """
        Отправка рассылок на почтовые адреса клиентов.
        """

        zone = timezone.get_current_timezone()
        current_datetime = datetime.now(zone)
        mailings = Mailing.objects.filter(
            datetime_first_mailing__lte=current_datetime, status=Mailing.Status.STARTED
        )
        for mailing in mailings:
            try:
                self.send_mailing(mailing)
            except Exception as e:
                self.stderr.write(f"Ошибка отправки рассылки {mailing.id}: {e}")

    def send_mailing(self, mailing):
        """
        Отправка рассылки почтовым адресам клиентов.
        """
        subject = mailing.message.subject
        content = mailing.message.content

        send_mail(
            subject=subject,
            message=content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[client.email for client in mailing.clients.all()],
        )
