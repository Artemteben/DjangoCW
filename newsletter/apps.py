import logging
import threading
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from time import sleep

logger = logging.getLogger(__name__)


class NewsletterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "newsletter"

    def ready(self):
        """
        Запускает планировщик рассылок при старте приложения.
        """
        logger.debug("NewsletterConfig.ready() начался")

        def start_scheduler():
            try:
                from newsletter.management.commands.start_scheduler import Command

                # Добавляем проверку готовности миграций
                logger.info("Запуск APScheduler из apps.py.")
                Command().handle()
            except ImportError as e:
                logger.error(f"Ошибка импорта модуля start_scheduler: {e}")
            except Exception as e:
                logger.error(f"Ошибка при запуске планировщика: {e}")

        def run_scheduler_with_delay():
            sleep(2)  # Задержка для предотвращения конфликта с миграциями
            start_scheduler()

        # Подключаем сигнал post_migrate для запуска планировщика после завершения миграций
        post_migrate.connect(
            lambda sender, **kwargs: threading.Thread(target=run_scheduler_with_delay, daemon=True).start(),
            sender=self,
        )
