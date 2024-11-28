import logging

from django.core.management.base import BaseCommand

from newsletter.tasks import (
    scheduler_started,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)



class Command(BaseCommand):
    help = "Запуск планировщика рассылок APScheduler."

    def handle(self, *args, **options):
        logger.info(f"Запуск планировщика")
        scheduler_started()

