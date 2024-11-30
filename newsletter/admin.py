from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import Mailing

from newsletter.models import Client, Mailing, Message, MailingAttempt

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("email", "fullname", "phone_number", "comment")
    search_fields = ("email", "fullname", "phone_number")
    list_filter = ("email", "fullname", "phone_number")

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("datetime_first_mailing", "frequency", "status")
    search_fields = ("message",)
    list_filter = ("frequency", "status", "datetime_first_mailing")

# Создание группы и назначение разрешений
manager_group, created = Group.objects.get_or_create(name='Manager')
manager_group.permissions.add(
    Permission.objects.get(codename='can_view_user'),
    Permission.objects.get(codename='can_change_user')
)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "content",
    )
    search_fields = ("subject",)

@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "datetime_attempt",
        "status",
    )
    list_filter = ("datetime_attempt", "status")
