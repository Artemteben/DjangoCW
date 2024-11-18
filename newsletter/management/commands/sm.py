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




def send_mailing():
    logger.info("Запуск функции send_mailing")
    logger.info("Функция send_mailing запущена.")
    zone = timezone.get_current_timezone()
    current_datetime = datetime.now(zone)
    mailings = Mailing.objects.filter(
        datetime_first_mailing__lte=current_datetime, status=Mailing.Status.CREATED
    )
    for mailing in mailings:
        logger.info("цикл send_mailing запущена.")
        try:
            subject = mailing.message.subject
            content = mailing.message.content
            logger.info(
                f"Отправка рассылки {mailing.id} клиентам: {[client.email for client in mailing.clients.all()]}"
            )
            send_mail(
                subject=subject,
                message=content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email for client in mailing.clients.all()],
            )
            logger.info(f"Рассылка {mailing} отправлена успешно.")
            Mailing.Status = "started"
            MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение отправлено успешно"
                )
        except Exception as e:
            logger.error(f"Ошибка отправки рассылки {mailing}: {e}")
            MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.FAILED,
                    server_response="Ошибка")




# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
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


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_mailing,
            trigger=self.get_cron_trigger(send_mailing),  # Every 10 seconds
            id="Mailing",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Добавлена задача 'send_mailing'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

    def get_cron_trigger(self, mailing):
        """
        Устанавливает интервал выполнения для конкретной рассылки на основе ее частоты.
        """
        current_datetime = timezone.now()
        if mailing.frequency == Mailing.Frequency.DAY:
            return CronTrigger(day="1", hour=current_datetime.hour + 1, minute=current_datetime.minute + 1)
        elif mailing.frequency == Mailing.Frequency.WEEK:
            return CronTrigger(week="1", hour=current_datetime.hour, minute=current_datetime.minute)  # каждое воскресенье
        elif mailing.frequency == Mailing.Frequency.MONTH:
            return CronTrigger(month="1", hour=current_datetime.hour, minute=current_datetime.minute)  # первое число каждого месяца