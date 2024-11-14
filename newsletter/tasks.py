# tasks.py
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from newsletter.models import Mailing, MailingAttempt
from newsletter.utils import send_mailing  # Функция, которая отправляет рассылки

# Настройка логирования
logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_send_mailings, "interval", minutes=1
    )  # Запуск каждые 1 мин.
    scheduler.start()


def check_and_send_mailings():
    current_time = timezone.now()
    mailings = Mailing.objects.filter(
        datetime_first_mailing__lte=current_time, status=Mailing.Status.CREATED
    )

    for mailing in mailings:
        # Получаем последнюю попытку рассылки
        last_attempt = mailing.attempts.last()

        # Проверяем, есть ли предыдущая попытка и прошло ли достаточно времени
        if last_attempt:
            # Проверка, прошло ли нужное количество времени (например, 1 час)
            time_diff = current_time - last_attempt.datetime
            if time_diff.total_seconds() < mailing.interval * 60:
                logger.info(
                    f"Skipping mailing {mailing.id}, not enough time passed since last attempt."
                )
                continue  # Пропускаем рассылку, если не прошло достаточно времени
        else:
            # Если нет предыдущей попытки, можно отправить рассылку
            logger.info(
                f"First attempt for mailing {mailing.id}. Proceeding with sending."
            )

        try:
            # Используем вашу утилиту для отправки рассылки
            send_mailing(mailing)  # Эта функция должна быть реализована в utils.py

            # После отправки можно обновить статус рассылки
            mailing.status = Mailing.Status.STARTED
            mailing.datetime_last_mailing = current_time
            mailing.save()

            logger.info(f"Mailing {mailing.id} started successfully.")
            mailing.attempts.create(
                status=MailingAttempt.Status.SUCCESS, server_response=str("OK")
            )
        except Exception as e:
            logger.error(f"Error sending mailing {mailing.id}: {str(e)}")
            # Запись попытки с ошибкой
            mailing.attempts.create(
                status=MailingAttempt.Status.FAILED, server_response=str(e)
            )

