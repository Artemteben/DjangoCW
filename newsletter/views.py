from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView,
)
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from blog.models import Blog
from newsletter.models import Client, Mailing, Message, MailingAttempt
from newsletter.forms import ClientForm, CreateMailingForm, UpdateMailingForm, MessageForm


# Декоратор для применения кэширования ко всем представлениям
def apply_cache_to_view(view_func):
    return method_decorator(cache_page(60 * 15))(view_func)


# Список клиентов

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "newsletter/client_list.html"


@method_decorator(apply_cache_to_view, name='dispatch')  # Применение кэширования
class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = "newsletter/client_detail.html"


# Редактирование клиента
class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm  # Использование формы
    template_name = "newsletter/client_form.html"
    permission_required = 'newsletter.change_client'  # Требуем разрешение на изменение клиента

    def get_success_url(self):
        return reverse("newsletter:client_detail", args=[self.object.pk])


# Удаление клиента
class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    template_name = "newsletter/client_confirm_delete.html"
    success_url = reverse_lazy("newsletter:client_list")
    permission_required = 'newsletter.delete_client'  # Требуем разрешение на удаление клиента


# Создание клиента
class ClientCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm  # Использование формы
    template_name = "newsletter/client_form.html"
    success_url = reverse_lazy("newsletter:client_list")
    permission_required = 'newsletter.add_client'  # Требуем разрешение на создание клиента


# Список рассылок

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "newsletter/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        # Возвращаем только рассылки текущего пользователя
        return Mailing.objects.filter(author=self.request.user)



class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "newsletter/mailing_detail.html"


# Редактирование рассылки
class MailingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mailing
    form_class = UpdateMailingForm  # Использование формы
    template_name = "newsletter/mailing_form.html"
    permission_required = 'newsletter.change_mailing'  # Требуем разрешение на изменение рассылки

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("newsletter:mailing_detail", args=[self.object.pk])



# Создание рассылки
class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = CreateMailingForm
    template_name = "newsletter/mailing_form.html"
    success_url = reverse_lazy("newsletter:mailing_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Передаем текущего пользователя в форму
        return kwargs

    def form_valid(self, form):
        # Устанавливаем текущего пользователя как автора рассылки
        form.instance.author = self.request.user
        return super().form_valid(form)

# Удаление рассылки
class MailingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Mailing
    template_name = "newsletter/mailing_confirm_delete.html"
    success_url = reverse_lazy("newsletter:mailing_list")
    permission_required = 'newsletter.delete_mailing'  # Требуем разрешение на удаление рассылки

    def get_context_data(self, **kwargs):
        """
        Переопределяем функцию для отображения
        клиентов этой рассылки.
        """
        context = super().get_context_data(**kwargs)
        clients = list(self.object.clients.all())
        context["clients"] = ", ".join([str(client) for client in clients])
        return context


# Список сообщений

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "newsletter/message_list.html"



class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "newsletter/message_detail.html"


# Редактирование сообщения
class MessageUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm  # Использование формы
    template_name = "newsletter/message_form.html"
    success_url = reverse_lazy("newsletter:message_list")
    permission_required = 'newsletter.change_message'  # Требуем разрешение на изменение сообщения


# Создание сообщения
class MessageCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm  # Использование формы
    template_name = "newsletter/message_form.html"
    success_url = reverse_lazy("newsletter:message_list")
    permission_required = 'newsletter.add_message'  # Требуем разрешение на создание сообщения


# Удаление сообщения
class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Message
    template_name = "newsletter/message_confirm_delete.html"
    success_url = reverse_lazy("newsletter:message_list")
    permission_required = 'newsletter.delete_message'  # Требуем разрешение на удаление сообщения


@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "newsletter/mailing_attempt_list.html"

    def get_queryset(self):
        # Загружаем связанные попытки рассылки для каждого объекта Mailing
        return MailingAttempt.objects.select_related("mailing").all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()  # Общее количество рассылок
        context["active_mailings"] = Mailing.objects.filter(
            status=Mailing.Status.STARTED
        ).count()  # Количество активных рассылок
        context["unique_clients"] = Client.objects.distinct().count()  # Количество уникальных клиентов
        context["random_blogs"] = Blog.objects.filter(published=True).order_by('?')[:3]  # Случайные блоги
        return context