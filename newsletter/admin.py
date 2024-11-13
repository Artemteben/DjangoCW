from django.contrib import admin

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
