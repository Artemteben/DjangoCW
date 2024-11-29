from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {"blank": True, "null": True}


class User(AbstractUser):
    """
    Модель пользователя.python manage.py migrate

    """

    username = None
    email = models.EmailField(
        unique=True,
        verbose_name="Электронная почта",
        help_text="Укажите электронную почту",
    )
    password = models.CharField(
        max_length=255, verbose_name="Пароль", help_text="Укажите пароль"
    )
    avatar = models.ImageField(
        upload_to="users/",
        verbose_name="Фото",
        help_text="Загрузите фото пользователя",
        **NULLABLE
    )
    token = models.CharField(
        max_length=100, verbose_name="Токен", help_text="Укажите токен", **NULLABLE
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_user", "Can view user"),
            ("can_change_user", "Can change user"),
        ]
