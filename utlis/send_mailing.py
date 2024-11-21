# # import logging
# # from datetime import datetime
# #
# # from apscheduler.schedulers.background import BackgroundScheduler
# # from apscheduler.triggers.cron import CronTrigger
# # from django.conf import settings
# # from django.core.mail import send_mail
# # from django.core.management.base import BaseCommand
# # from django.utils import timezone
# # from django_apscheduler.jobstores import DjangoJobStore
# #
# # from newsletter.models import Mailing
# #
# # # Настройка логирования
# # logger = logging.getLogger(__name__)
# # logging.basicConfig(level=logging.DEBUG)
# #
# #
# # def send_mailing():
# #     """
# #     Отправка рассылок на почтовые адреса клиентов.
# #     """
# #     zone = timezone.get_current_timezone()
# #     current_datetime = datetime.now(zone)
# #     mailings = Mailing.objects.filter(
# #         datetime_first_mailing__lte=current_datetime, status=Mailing.Status.STARTED
# #     )
# #     for mailing in mailings:
# #         try:
# #             subject = mailing.message.subject
# #             content = mailing.message.content
# #
# #             send_mail(
# #                 subject=subject,
# #                 message=content,
# #                 from_email=settings.EMAIL_HOST_USER,
# #                 recipient_list=[client.email for client in mailing.clients.all()],
# #             )
# #         except Exception as e:
# #             f"Ошибка отправки рассылки {mailing.id}: {e}"
# #
# #
# # class Command(BaseCommand):
# #     help = "Отправка рассылок"
# #
# #     def start(self, send_mailing):
# #         # Создание планировщика
# #         scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
# #         scheduler.add_job(send_mailing, "interval", seconds=10)
# #         scheduler.start()
# #         return scheduler
# #
# #     def handle(self, *args, **options):
# #         # Создание планировщика
# #         # scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
# #         scheduler.add_jobstore(DjangoJobStore(), "default")
# #
# #         # Получение всех рассылок с начальным статусом
# #         mailings = Mailing.objects.filter(status=Mailing.Status.STARTED)
# #         logger.debug(f"Найдено {mailings.count()} рассылок для отправки.")
# #
# #         # Добавление задач в планировщик
# #         self.scheduler.add_job(
# #             send_mailing,
# #             trigger=self.check_interval(),  # Every 10 seconds
# #             id="send_mailing",  # The `id` assigned to each job MUST be unique
# #             max_instances=1,
# #             replace_existing=True,
# #         )
# #         try:
# #             logger.debug(f"Запуск планировщика...")
# #             scheduler.start(send_mailing)
# #         except KeyboardInterrupt:
# #             scheduler.shutdown()
# #             logger.debug("Планировщик остановлен.")
# #
# #     def check_interval(self):
# #         zone = timezone.get_current_timezone()
# #         current_datetime = datetime.now(zone)
# #         mailings = Mailing.objects.filter(
# #             datetime_first_mailing__lte=current_datetime, status=Mailing.Status.STARTED
# #         )
# #         for mailing in mailings:
# #             if mailing.Frequency.DAY:
# #                 return CronTrigger(
# #                     day=1, hour=current_datetime.hour, minute=current_datetime.minute
# #                 )
# #             elif mailing.Frequency.WEEK:
# #                 return CronTrigger(week=1)
# #             elif mailing.Frequency.MONTH:
# #                 return CronTrigger(month=1)
#
#
# #
# import logging
# from datetime import datetime
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.conf import settings
# from django.core.mail import send_mail
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from django_apscheduler.jobstores import DjangoJobStore
# from newsletter.models import Mailing
# from apscheduler.triggers.interval import IntervalTrigger
#
# # Настройка логирования
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
#
#
# def send_mailing():
#     logger.info("Запуск функции send_mailing")
#     logger.info("Функция send_mailing запущена.")
#     zone = timezone.get_current_timezone()
#     current_datetime = datetime.now(zone)
#     mailings = Mailing.objects.filter(
#         datetime_first_mailing__lte=current_datetime, status=Mailing.status.STARTED
#     )
#     for mailing in mailings:
#         try:
#             subject = mailing.message.subject
#             content = mailing.message.content
#             logger.info(
#                 f"Отправка рассылки {mailing.id} клиентам: {[client.email for client in mailing.clients.all()]}"
#             )
#             send_mail(
#                 subject=subject,
#                 message=content,
#                 from_email=settings.EMAIL_HOST_USER,
#                 recipient_list=[client.email for client in mailing.clients.all()],
#             )
#             logger.info(f"Рассылка {mailing.id} отправлена успешно.")
#         except Exception as e:
#             logger.error(f"Ошибка отправки рассылки {mailing.id}: {e}")
#
#
# #
# # class Command(BaseCommand):
# #     help = "Запускает планировщик для отправки рассылок."
# #
# #     def start_scheduler(self):
# #         scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
# #         scheduler.add_jobstore(DjangoJobStore(), "default")
# #         return scheduler
# #
# #     def handle(self, *args, **options):
# #         # Создание планировщика
# #         scheduler = self.start_scheduler()
# #
# #         mailings = Mailing.objects.filter(status=Mailing.Status.STARTED)
# #         for mailing in mailings:
# #             # Добавление задачи с динамическим расписанием
# #             scheduler.add_job(
# #                 send_mailing,
# #                 # trigger=self.get_cron_trigger(mailing),
# #                 trigger=IntervalTrigger(seconds=10),
# #                 id=f"send_mailing_{mailing.id}",
# #                 max_instances=1,
# #                 replace_existing=True,
# #             )
# #
# #         try:
# #             logger.debug("Запуск планировщика...")
# #             scheduler.start()
# #         except KeyboardInterrupt:
# #             scheduler.shutdown()
# #             logger.debug("Планировщик остановлен.")
# #
# #     def get_cron_trigger(self, mailing):
# #         """
# #         Устанавливает интервал выполнения для конкретной рассылки на основе ее частоты.
# #         """
# #         current_datetime = timezone.now()
# #         if mailing.frequency == Mailing.Frequency.DAY:
# #             return CronTrigger(day="1", hour=current_datetime.hour+1, minute=current_datetime.minute+1)
# #         elif mailing.frequency == Mailing.Frequency.WEEK:
# #             return CronTrigger(week="1", hour=current_datetime.hour, minute=current_datetime.minute)  # каждое воскресенье
# #         elif mailing.frequency == Mailing.Frequency.MONTH:
# #             return CronTrigger(month="1", hour=current_datetime.hour, minute=current_datetime.minute)  # первое число каждого месяца
#
#
# # from django.core.management.base import BaseCommand
# # from django.utils import timezone
# # from apscheduler.schedulers.background import BackgroundScheduler
# # from django_apscheduler.jobstores import DjangoJobStore, MemoryJobStore
# # from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
# # from newsletter.models import Mailing, MailingAttempt, Client
# # from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# # import logging
# #
# # # Настроим базовое логирование
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)
# #
# #
# # def send_mailing(mailing_id):
# #     """
# #     Основная функция для отправки рассылок.
# #     """
# #     logger.info(f"Запуск функции send_mailing для рассылки {mailing_id}")
# #     try:
# #         mailing = Mailing.objects.get(id=mailing_id)
# #         clients = mailing.clients.all()
# #         client_emails = [client.email for client in clients]
# #
# #         logger.info(f"Отправка рассылки '{mailing_id}' клиентам: {client_emails}")
# #
# #         # Имитируем процесс отправки
# #         for client in clients:
# #             MailingAttempt.objects.create(
# #                 mailing=mailing,
# #                 datetime_attempt=timezone.now(),
# #                 status=MailingAttempt.Status.SUCCESS,
# #                 server_response="Сообщение отправлено успешно"
# #             )
# #         logger.info(f"Рассылка {mailing_id} отправлена успешно.")
# #     except Exception as e:
# #         logger.error(f"Ошибка при отправке рассылки {mailing_id}: {str(e)}")
# #         for client in clients:
# #             MailingAttempt.objects.create(
# #                 mailing=mailing,
# #                 datetime_attempt=timezone.now(),
# #                 status=MailingAttempt.Status.FAILED,
# #                 server_response="Ошибка")
#
#
# # class Command(BaseCommand):
# #     help = "Команда для запуска планировщика рассылки сообщений"
# #
# #     def handle(self, *args, **options):
# #         logger.info("Запуск команды send_mailing")
# #         scheduler = self.start_scheduler()
# #
# #         # Добавляем задачи для всех рассылок, которые должны выполняться
# #         mailings = Mailing.objects.filter(status=Mailing.Status.CREATED)
# #         for mailing in mailings:
# #             # interval_seconds = self.get_interval_seconds(mailing.frequency)
# #             interval_seconds = 10
# #             scheduler.add_job(
# #                 send_mailing,
# #                 trigger='interval',
# #                 seconds=interval_seconds,
# #                 args=[mailing.id],
# #                 id=f"send_mailing_{mailing.id}"
# #             )
# #             logger.info(f"Задача для рассылки {mailing.id} добавлена с частотой {mailing.frequency}")
# #
# #         # Запускаем планировщик
# #         scheduler.start()
# #         logger.info("Планировщик запущен и готов к выполнению задач.")
# #
# #     # def start_scheduler(self):
# #     #     scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
# #     #     scheduler.add_jobstore(MemoryJobStore(), "default")
# #     #     scheduler.add_listener(self.log_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
# #     #     return scheduler
# #
# #     def start_scheduler(self):
# #         scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
# #         scheduler.add_jobstore(SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'), "default")
# #         scheduler.add_listener(self.log_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
# #         return scheduler
# #     def log_event(self, event):
# #         if event.exception:
# #             logger.error(f"Ошибка выполнения задачи {event.job_id}: {event.exception}")
# #         else:
# #             logger.info(f"Задача {event.job_id} выполнена успешно")
# #
# #     def get_interval_seconds(self, frequency):
# #         if frequency == 'day':
# #             return 86400
# #         elif frequency == 'week':
# #             return 604800
# #         elif frequency == 'month':
# #             return 2592000
# #         return 3600  # значение по умолчанию: 1 час
