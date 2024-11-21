import logging
from datetime import timedelta

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from newsletter.models import Mailing, MailingAttempt
from newsletter.tasks import (
    delete_old_job_executions,
    schedule_future_mailing,
    scheduler_started,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):
    help = "Запуск планировщика рассылок APScheduler."

    def handle(self, *args, **options):
        scheduler_started()
        # scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        # scheduler.add_jobstore(DjangoJobStore(), "default")
        #
        # # Планирование будущих рассылок
        # for mailing in Mailing.objects.filter(
        #     datetime_first_mailing__gt=timezone.now(),
        #     status=Mailing.Status.CREATED,
        # ):
        #     schedule_future_mailing(scheduler, mailing)
        #
        # # Задача для удаления старых записей
        # scheduler.add_job(
        #     delete_old_job_executions,
        #     trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),
        #     id="delete_old_job_executions",
        #     replace_existing=True,
        # )
        #
        # logger.info("Запуск планировщика...")
        # try:
        #     scheduler.start()
        # except KeyboardInterrupt:
        #     logger.info("Остановка планировщика...")
        #     scheduler.shutdown()
        #     logger.info("Планировщик успешно остановлен!")
