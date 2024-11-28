import logging
from django.core.management.base import BaseCommand
from newsletter.tasks import scheduler_started
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запуск планировщика"

    def handle(self, *args, **kwargs):
        logger.info("Запуск планировщика вручную...")
        scheduler = BackgroundScheduler(timezone='UTC')
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.start()
        logger.info("Планировщик запущен.")
