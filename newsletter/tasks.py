import logging
from datetime import timedelta
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from newsletter.models import Mailing, MailingAttempt
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
from newsletter.tasks import delete_old_job_executions, schedule_future_mailing

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def delete_old_job_executions(max_age=604_800):
    """
    Удаление старых записей задач APScheduler из базы данных.
    :param max_age: Максимальный возраст записей в секундах. По умолчанию: 7 дней.
    """
    threshold = timezone.now() - timedelta(seconds=max_age)
    try:
        DjangoJobExecution.objects.filter(run_time__lte=threshold).delete()
    except Exception as e:
        logger.error(f"Ошибка при удалении старых записей задач: {e}")


def get_cron_trigger(mailing):
    """
    Создание CronTrigger на основе частоты рассылки.
    """
    if mailing.frequency == Mailing.Frequency.DAY:
        return CronTrigger(hour=0, minute=0)  # Ежедневно в полночь
    elif mailing.frequency == Mailing.Frequency.WEEK:
        return CronTrigger(day_of_week="mon", hour=0, minute=0)  # Еженедельно
    elif mailing.frequency == Mailing.Frequency.MONTH:
        return CronTrigger(day=1, hour=0, minute=0)  # Ежемесячно
    else:
        logger.error(
            f"[Рассылка ID {mailing.id}] Неизвестная частота: {mailing.frequency}"
        )
        raise ValueError(f"Неизвестная частота рассылки: {mailing.frequency}")


def schedule_future_mailing(scheduler, mailing):
    """
    Планирование рассылки с учётом даты завершения.
    :param scheduler: Объект планировщика
    :param mailing: Экземпляр рассылки
    """
    now = timezone.now()
    # Проверка на повторное добавление задачи
    if scheduler.get_job(f"send_mailing_{mailing.id}_frequency"):
        logger.info(f"Задача для рассылки {mailing.id} уже запланирована.")
        return

    # Если время последней рассылки уже истекло, не планируем
    if mailing.datetime_last_mailing and mailing.datetime_last_mailing <= now:
        logger.info(
            f"Рассылка ID {mailing.id} пропущена, так как дата завершения уже истекла."
        )
        return

    # Регулярные рассылки
    if mailing.frequency in [
        Mailing.Frequency.DAY,
        Mailing.Frequency.WEEK,
        Mailing.Frequency.MONTH,
    ]:
        trigger = get_cron_trigger(mailing)
        if trigger:
            scheduler.add_job(
                send_mailing,
                trigger=trigger,
                id=f"send_mailing_{mailing.id}_frequency",
                args=[mailing.id],
                replace_existing=True,
                end_date=mailing.datetime_last_mailing,  # Завершаем после этой даты
            )
            logger.info(
                f"Регулярная рассылка ID {mailing.id} запланирована "
                f"с частотой {mailing.frequency}, завершение {mailing.datetime_last_mailing}."
            )

    # Разовая задача
    elif mailing.datetime_first_mailing > now:
        trigger = CronTrigger(
            year=mailing.datetime_first_mailing.year,
            month=mailing.datetime_first_mailing.month,
            day=mailing.datetime_first_mailing.day,
            hour=mailing.datetime_first_mailing.hour,
            minute=mailing.datetime_first_mailing.minute,
            second=0,
        )
        scheduler.add_job(
            send_mailing,
            trigger=trigger,
            id=f"send_mailing_{mailing.id}_once",
            args=[mailing.id],
            replace_existing=True,
        )
        logger.info(
            f"Разовая рассылка ID {mailing.id} запланирована на {mailing.datetime_first_mailing}."
        )


def send_mailing(mailing_id):
    """
    Отправка рассылки для указанного ID.
    """
    try:
        mailing = Mailing.objects.get(id=mailing_id)
        now = timezone.now()

        # Проверка на истечение даты завершения
        if mailing.datetime_last_mailing and now > mailing.datetime_last_mailing:
            logger.info(
                f"Рассылка ID {mailing.id} остановлена, так как дата завершения истекла."
            )
            return

        # Проверка на наличие клиентов
        if not mailing.clients.exists():
            logger.info(f"Рассылка ID {mailing.id} не имеет клиентов. Завершение.")
            mailing.status = Mailing.Status.FINISHED
            mailing.save()
            return

        # Обновляем статус рассылки
        if mailing.status != Mailing.Status.STARTED:
            mailing.status = Mailing.Status.STARTED
            mailing.save()

        # Счетчики
        success_count, fail_count = 0, 0

        # Цикл по клиентам
        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.content,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[client.email],
                )
                success_count += 1
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.SUCCESS,
                    server_response="Сообщение отправлено успешно",
                )
            except Exception as e:
                fail_count += 1
                logger.error(
                    f"[Рассылка ID {mailing.id}] Ошибка для клиента {client.email}: {e}"
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    datetime_attempt=timezone.now(),
                    status=MailingAttempt.Status.FAILED,
                    server_response=str(e),
                )

        # Проверяем, все ли клиенты обработаны
        if success_count + fail_count == mailing.clients.count():
            mailing.status = Mailing.Status.FINISHED
            mailing.save()

        # Логируем результаты
        logger.info(
            f"[Рассылка ID {mailing.id}] Успешно отправлено: {success_count}, Ошибки: {fail_count}"
        )

    except Mailing.DoesNotExist:
        logger.error(f"Рассылка ID {mailing_id} не найдена.")


def scheduler_started():

    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Планирование будущих рассылок
    for mailing in Mailing.objects.filter(
        datetime_first_mailing__gt=timezone.now(),
        status=Mailing.Status.CREATED,
    ):
        schedule_future_mailing(scheduler, mailing)

    # Задача для удаления старых записей
    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(day_of_week="mon", hour=0, minute=0),
        id="delete_old_job_executions",
        replace_existing=True,
    )

    logger.info("Запуск планировщика...")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Остановка планировщика...")
        scheduler.shutdown()
        logger.info("Планировщик успешно остановлен!")
