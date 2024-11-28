from django.contrib import admin
from django.contrib.admin import ModelAdmin

from blog.models import Blog


@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    """
    Регистрирует модель Блога в админке.
    """
    list_display = (
        'id', 'title', 'text', 'image', 'views_count', 'date', 'date_update'
    )
    list_filter = ('title', 'views_count', 'date', 'date_update')
    search_fields = ('title', 'text')
