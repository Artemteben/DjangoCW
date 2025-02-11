from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from blog.forms import BlogCreateForm
from blog.models import Blog

from django.shortcuts import render
from .models import Blog
from newsletter.models import Mailing, Client


class BlogCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):

    model = Blog
    form_class = BlogCreateForm
    success_url = reverse_lazy("blog:list")
    permission_required = "blog.can_add_blog"
    extra_context = {"title": "Создание статьи"}


class BlogUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    model = Blog
    form_class = BlogCreateForm
    success_url = reverse_lazy("blog:list")
    permission_required = "blog.can_change_blog"
    extra_context = {"title": "Редактирование статьи"}


class BlogDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):

    model = Blog
    permission_required = "blog.can_view_blog"
    extra_context = {"title": "Просмотр статьи"}


class BlogDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):


    model = Blog
    success_url = reverse_lazy("blog:list")
    permission_required = "blog.can_delete_blog"
    extra_context = {"title": "Удаление статьи"}


class BlogListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    model = Blog
    permission_required = "blog.can_view_blog"
    extra_context = {"title": "Список статей"}
