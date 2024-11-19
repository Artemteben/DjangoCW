from django.db.models.signals import post_save
from django.dispatch import receiver

from config import settings
from newsletter.models import Mailing
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from newsletter.management.commands.start_scheduler import schedule_future_mailing

@receiver(post_save, sender=Mailing)
def schedule_mailing_on_save(sender, instance, created, **kwargs):
    """
    Планирование рассылки при её создании или обновлении.
    """
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")
    schedule_future_mailing(scheduler, instance)
    scheduler.shutdown()
