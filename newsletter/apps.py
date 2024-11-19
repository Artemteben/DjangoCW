import logging
import threading
from time import sleep
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class NewsletterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsletter"

    # def ready(self):
    #     """
    #     Запускает планировщик рассылок при старте приложения.
    #     """
    #     from newsletter.management.commands.run_scheduler import Command
    #
    #     def start_scheduler():
    #         """
    #         Обертка для запуска команды планировщика в отдельном потоке.
    #         """
    #         try:
    #             sleep(2)  # Задержка для предотвращения конфликта с миграциями
    #             logger.info("Запуск APScheduler из apps.py.")
    #             Command().handle()
    #         except Exception as e:
    #             logger.error(f"Ошибка при запуске планировщика: {e}")
    #
    #     # Запуск планировщика в отдельном потоке
    #     threading.Thread(target=start_scheduler, daemon=True).start()
