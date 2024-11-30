import logging
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from newsletter.models import Mailing, MailingAttempt

logger = logging.getLogger(__name__)


def delete_old_job_executions(max_age=604_800):
    """
    Удаление старых записей APScheduler.
    :param max_age: Максимальный возраст в секундах (по умолчанию 7 дней).
    """
    threshold = timezone.now() - timedelta(seconds=max_age)
    try:
        logger.info("Удаление старых записей APScheduler.")
        DjangoJobExecution.objects.filter(run_time__lte=threshold).delete()
    except Exception as e:
        logger.error(f"Ошибка при удалении старых записей: {e}")


def get_cron_trigger(mailing):
    """
    Генерация CronTrigger для частоты рассылки.
    """
    if mailing.frequency == Mailing.Frequency.DAY:
        return CronTrigger(hour=0, minute=0)
    elif mailing.frequency == Mailing.Frequency.WEEK:
        return CronTrigger(day_of_week="mon", hour=0, minute=0)
    elif mailing.frequency == Mailing.Frequency.MONTH:
        return CronTrigger(day=1, hour=0, minute=0)
    else:
        logger.error(f"Неизвестная частота рассылки: {mailing.frequency}")
        logger.error("Частота рассылки будет минутная")
        return CronTrigger(minute="1")


def schedule_future_mailing(scheduler, mailing):
    """
    Планирование задач рассылки.
    """
    now = timezone.now()
    if scheduler.get_job(f"send_mailing_{mailing.id}"):
        logger.info(f"Задача для рассылки {mailing.id} уже существует.")
        return

    # Проверяем, если дата первой рассылки уже прошла
    if mailing.datetime_first_mailing <= now:
        logger.info(f"Рассылка {mailing.id} пропущена: время первой рассылки уже прошло.")
        return

    # Запланировать задачу на дату и время первой рассылки
    scheduler.add_job(
        send_initial_mailing,
        trigger=DateTrigger(run_date=mailing.datetime_first_mailing),
        id=f"initial_send_mailing_{mailing.id}",
        args=[mailing.id],
        replace_existing=True,
    )
    logger.info(f"Запланирована начальная рассылка {mailing.id} на {mailing.datetime_first_mailing}.")


def send_initial_mailing(mailing_id):
    """
    Выполнение начальной рассылки и запуск регулярной задачи.
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        now = timezone.now()

        # Убедимся, что рассылка активна и не завершена
        if mailing.status != Mailing.Status.STARTED:
            mailing.status = Mailing.Status.STARTED
            mailing.save()

        # Выполняем рассылку
        send_mailing(mailing_id)

        # После первой отправки запустить периодическую задачу
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        trigger = get_cron_trigger(mailing)
        if trigger:
            scheduler.add_job(
                send_mailing,
                trigger=trigger,
                id=f"send_mailing_{mailing.id}",
                args=[mailing_id],
                replace_existing=True,
                end_date=mailing.date_time_last_mailing,
            )
            logger.info(f"Запланирована регулярная рассылка {mailing.id} с частотой {mailing.frequency}.")
        scheduler.start()

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена.")


def send_mailing(mailing_id):
    """
    Отправка рассылки по указанному ID.
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        if mailing.status != Mailing.Status.STARTED:
            mailing.status = Mailing.Status.STARTED
            mailing.save()

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение успешно отправлено.",
                )
            except Exception as e:
                logger.error(f"Ошибка отправки для {client.email}: {e}")
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.FAILED,
                    server_response=str(e),
                )

        mailing.status = Mailing.Status.FINISHED
        mailing.save()
    except Mailing.DoesNotExist:
        logger.error(f"Рассылка с ID {mailing_id} не найдена.")


def scheduler_started():
    logger.info("Инициализация планировщика...")
    try:
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        logger.info("Добавлен DjangoJobStore.")

        # Планируем все задачи с учетом datetime_first_mailing
        for mailing in Mailing.objects.filter(
                status=Mailing.Status.CREATED
        ):
            logger.info(f"Обрабатываем рассылку ID: {mailing.id}.")
            schedule_future_mailing(scheduler, mailing)

        # Удаление старых записей
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),
            id="delete_old_job_executions",
            replace_existing=True,
        )
        logger.info("Задача для удаления старых записей добавлена.")

        scheduler.start()
        logger.info("Планировщик успешно запущен.")
    except Exception as e:
        logger.error(f"Ошибка при запуске планировщика: {e}")
