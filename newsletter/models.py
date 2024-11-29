from django.db import models
from django.utils import timezone

from users.models import User

NULLABLE = {"blank": True, "null": True}


class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="email")
    fullname = models.CharField(max_length=250, verbose_name="ФИО")
    phone_number = models.CharField(max_length=15, unique=True, **NULLABLE)
    comment = models.TextField(verbose_name="Комментарий", **NULLABLE)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
        **NULLABLE
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"{self.fullname}, {self.email}"


class Mailing(models.Model):
    class Frequency(models.TextChoices):
        DAY = "day", "ежедневно"
        WEEK = "week", "еженедельно"
        MONTH = "month", "ежемесячно"

    class Status(models.TextChoices):
        CREATED = "CREATED", "Создана"
        STARTED = "STARTED", "Начата"
        FINISHED = "FINISHED", "Завершена"

    clients = models.ManyToManyField(
        Client, verbose_name="Клиенты"
    )  # Обесепечение связи одно сообщенеи много вклиентов с помощью ManyToManyField
    message = models.ForeignKey(
        "Message", on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    datetime_first_mailing = models.DateTimeField(
        default=timezone.now, verbose_name="Дата начала рассылки"
    )
    date_time_last_mailing = models.DateTimeField(
        default=timezone.now,
        null=True,
        blank=True,
        verbose_name="Последний день рассылки",
    )
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
        verbose_name="Периодичность рассылки",
        **NULLABLE,
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name="Статус выполнения",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
        **NULLABLE
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return f"Рассылка {self.frequency} для {self.clients.all().count()} клиентов"


class Message(models.Model):
    subject = models.CharField(max_length=255, verbose_name="Тема сообщения")
    content = models.TextField(verbose_name="Содержание сообщения")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Укажите автора',
        **NULLABLE
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


class MailingAttempt(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Успешно"
        FAILED = "failed", "Неуспешно"

    mailing = models.ForeignKey(
        "Mailing",
        on_delete=models.CASCADE,
        verbose_name="Рассылка",
        related_name="attempts",
    )
    datetime_attempt = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата и время попытки рассылки",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.SUCCESS, **NULLABLE
    )
    server_response = models.TextField(**NULLABLE, verbose_name="Отклик сервера")

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"

    def __str__(self):
        return f"Attempt on {self.datetime_attempt} - {self.status}"
