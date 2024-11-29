from django.db import models

from newsletter.models import NULLABLE
from users.models import User


class Blog(models.Model):
    """
    Модель блога.
    """
    title = models.CharField(
        max_length=100, verbose_name="Заголовок", help_text="Напишите заголовок"
    )
    content = models.TextField(
        verbose_name="Текст статьи", help_text="Напишите текст статьи", **NULLABLE
    )
    image = models.ImageField(
        upload_to="blogs/",
        verbose_name="Изображение",
        help_text="Загрузите изображение",
        **NULLABLE
    )
    views = models.PositiveIntegerField(
        default=0,
        verbose_name="Количество просмотров",
        help_text="Укажите количество просмотров",
    )
    created_at = models.DateField(auto_now_add=True)
    date_update = models.DateField(auto_now=True)
    published = models.BooleanField(default=False)  # Статус публикации
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Укажите пользователя',
        **NULLABLE
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Блог"
        verbose_name_plural = "Блог"
        permissions = [
            ("can_add_blog", "Can add blog"),
            ("can_view_blog", "Can view blog"),
            ("can_change_blog", "Can change blog"),
            ("can_delete_blog", "Can delete blog"),
        ]
