from django.apps import AppConfig
import logging
# from newsletter.tasks import start_scheduler
from time import sleep

logger = logging.getLogger(__name__)


class NewsletterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsletter"

    # def ready(self):
    #     sleep(2)  # Задержка для старта
    #     start_scheduler()  # Функция старта задач
