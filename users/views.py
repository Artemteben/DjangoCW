import secrets

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from config.settings import EMAIL_HOST_USER

from . import forms
from .models import User


class UserLoginView(LoginView):
    """
    Класс отображения страницы входа в аккаунт.
    """
    form_class = forms.LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}


class UserRegisterView(CreateView):
    """
    Класс отображения страницы регистрации пользователя.
    """
    form_class = forms.UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:show_certificate')
    extra_context = {'title': 'Регистрация'}

    def form_valid(self, form):
        """
        Переопределяем функцию для отправки сообщения
        пользователя для проверки действительности почты.
        """
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http://{host}/users/email-confirm/{token}'
        send_mail(
            subject='Подтверждение почты',
            message=f'Перейдите по ссылке для подтверждения электронной почты {url}',
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verifications(request, token):
    """
    Функция для проверки подлинности пользователя.
    """
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return redirect(reverse_lazy('users:login'))


def show_certificate(request):
    """
    Функция для отображения справочной информации
    для входа в аккаунт.
    """
    return render(request, 'users/show_certificate.html')


class UserProfile(LoginRequiredMixin, UpdateView):
    """
    Класс отображения страницы профиля пользователя.
    """
    form_class = forms.UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')
    extra_context = {'title': 'Профиль'}

    def get_object(self, queryset=None):
        """
        Переопределяем функцию
        для получения текущего пользователя.
        """
        return self.request.user


class UserPasswordChangeView(PasswordChangeView):
    """
    Класс отображения страницы изменения пароля.
    """
    form_class = forms.UserPasswordChangeForm
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')
    extra_context = {'title': 'Восстановление пароля'}


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """
    Класс отображения страницы для редактирования профиля.
    """
    model = User
    success_url = reverse_lazy('users:list')
    extra_context = {'title': 'Профиль'}

    def get_form_class(self):
        """
        Переопределяем функцию для проверки
        принадлежности к текущему пользователю
        и правам.
        """
        user = self.request.user
        if self.object.email == user.email:
            return forms.UserProfileForm
        if user.has_perm('users.can_change_user'):
            return forms.UserModerProfileForm


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """
    Класс отображения страницы удаления профиля пользователя.
    """
    model = User
    success_url = reverse_lazy('users:list')
    extra_context = {'title': 'Удаление профиля'}


class UserListView(LoginRequiredMixin, ListView):
    """
    Класс отображения страницы списка пользователей.
    """
    model = User
    extra_context = {'title': 'Список пользователей'}
