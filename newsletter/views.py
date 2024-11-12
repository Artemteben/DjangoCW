from newsletter.models import Client, Mailing, Message
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView


# Список клиентов
class ClientListView(ListView):
    model = Client
    template_name = 'newsletter/client_list.html'


# Редактирование клиента
class ClientUpdateView(UpdateView):
    model = Client
    fields = '__all__'
    template_name = 'newsletter/client_form.html'

    def get_success_url(self):
        return reverse("newsletters:client_detail", args=[self.object.pk])


# Удаление клиента
class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'newsletter/client_confirm_delete.html'
    success_url = reverse_lazy("newsletters:client_list")


# Создание клиента
class ClientCreateView(CreateView):
    model = Client
    fields = '__all__'
    template_name = 'newsletter/client_form.html'
    success_url = reverse_lazy("newsletters:client_list")


# Список рассылок
class MailingListView(ListView):
    model = Mailing
    template_name = 'newsletter/mailing_list.html'


# Редактирование рассылки
class MailingUpdateView(UpdateView):
    model = Mailing
    fields = '__all__'
    template_name = 'newsletter/mailing_form.html'

    def get_success_url(self):
        return reverse("newsletters:mailing_detail", args=[self.object.pk])


# Создание рассылки
class MailingCreateView(CreateView):
    model = Mailing
    fields = ["status", "message", "frequency", "clients"]
    template_name = 'newsletter/mailing_form.html'
    success_url = reverse_lazy("newsletters:mailing_list")


# Удаление рассылки
class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'newsletter/mailing_confirm_delete.html'
    success_url = reverse_lazy("newsletters:mailing_list")


# Список сообщений
class MessageListView(ListView):
    model = Message
    template_name = 'newsletter/message_list.html'


# Редактирование сообщения
class MessageUpdateView(UpdateView):
    model = Message
    fields = '__all__'
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy("newsletters:message_list")


# Создание сообщения
class MessageCreateView(CreateView):
    model = Message
    fields = '__all__'
    template_name = 'newsletter/message_form.html'
    success_url = reverse_lazy("newsletters:message_list")


# Удаление сообщения
class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'newsletter/message_confirm_delete.html'
    success_url = reverse_lazy("newsletters:message_list")
