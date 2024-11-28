from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from blog.forms import BlogCreateForm
from blog.models import Blog


class BlogCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Модель создания статьи блога.
    """
    model = Blog
    form_class = BlogCreateForm
    success_url = reverse_lazy('blog:list')
    permission_required = 'blog.can_add_blog'
    extra_context = {'title': 'Создание статьи'}


class BlogUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Модель редактирования статьи блога.
    """
    model = Blog
    form_class = BlogCreateForm
    success_url = reverse_lazy('blog:list')
    permission_required = 'blog.can_change_blog'
    extra_context = {'title': 'Редактирование статьи'}


class BlogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Модель детального просмотра статьи блога.
    """
    model = Blog
    permission_required = 'blog.can_view_blog'
    extra_context = {'title': 'Просмотр статьи'}


class BlogDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    Модуль удаления статьи блога.
    """
    model = Blog
    success_url = reverse_lazy('blog:list')
    permission_required = 'blog.can_delete_blog'
    extra_context = {'title': 'Удаление статьи'}


class BlogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Модель вывода всех статей блога.
    """
    model = Blog
    permission_required = 'blog.can_view_blog'
    extra_context = {'title': 'Список статей'}
