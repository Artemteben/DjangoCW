# utils.py
from django.core.mail import send_mail
from django.conf import settings
from .models import MailingAttempt, Mailing
import pytz
from django.utils import timezone


def send_mailing(mailing):
    clients = mailing.clients.all()
    for client in clients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.content,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[client.email],
            )
            status = MailingAttempt.Status.SUCCESS
            server_response = "Message sent successfully"
        except Exception as e:
            status = MailingAttempt.Status.FAILED
            server_response = str(e)

        # Создание записи о попытке рассылки
        MailingAttempt.objects.create(
            mailing=mailing, status=status, server_response=server_response
        )

    # Обновить статус рассылки, если она завершена
    if mailing.frequency == Mailing.Frequency.DAILY:
        mailing.datetime_first_mailing += timezone.timedelta(days=1)
    elif mailing.frequency == Mailing.Frequency.WEEKLY:
        mailing.datetime_first_mailing += timezone.timedelta(weeks=1)
    elif mailing.frequency == Mailing.Frequency.MONTHLY:
        mailing.datetime_first_mailing += timezone.timedelta(weeks=4)
