from django.db import models

from newsletter.models import NULLABLE


class Blog(models.Model):
    """
    Модель блога.
    """
    title = models.CharField(
        max_length=100,
        verbose_name='Заголовок',
        help_text='Напишите заголовок'
    )
    text = models.TextField(
        verbose_name='Текст статьи',
        help_text='Напишите текст статьи',
        **NULLABLE
    )
    image = models.ImageField(
        upload_to='blogs/',
        verbose_name='Изображение',
        help_text='Загрузите изображение',
        **NULLABLE
    )
    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров',
        help_text='Укажите количество просмотров'
    )
    date = models.DateField(
        auto_now_add=True
    )
    date_update = models.DateField(
        auto_now=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Блог'
        verbose_name_plural = 'Блог'
        permissions = [
            ('can_add_blog', 'Can add blog'),
            ('can_view_blog', 'Can view blog'),
            ('can_change_blog', 'Can change blog'),
            ('can_delete_blog', 'Can delete blog')
        ]
