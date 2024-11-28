from django.apps import AppConfig
import os
import logging

logger = logging.getLogger(__name__)

class NewsletterConfig(AppConfig):
    name = "newsletter"

    def ready(self):
        logger.info("Инициализация NewsletterConfig.ready()")
        if os.environ.get("RUN_MAIN") == "true":
            from newsletter.tasks import scheduler_started
            scheduler_started()
        else:
            logger.info("RUN_MAIN не равен true, планировщик не будет запущен.")
