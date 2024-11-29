from django.contrib import admin
from .models import Blog

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'published', 'views')  # Какие поля отображать в списке
    list_filter = ('published', 'created_at')  # Фильтры
    search_fields = ('title', 'content')  # Поиск по этим полям
