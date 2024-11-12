from django.urls import path
from newsletter.apps import NewsletterConfig
from newsletter.views import (
    ClientListView,
    ClientDetailView,
    ClientCreateView,
    ClientDeleteView,
    ClientUpdateView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingDeleteView,
    MailingUpdateView,
    MessageListView,
    MessageDetailView,
    MessageUpdateView,
    MessageDeleteView,
    MessageCreateView,
)

app_name = NewsletterConfig.name

urlpatterns = [
    path("", ClientListView.as_view(), name="client_list"),
    path("client/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("client/create/", ClientCreateView.as_view(), name="client_create"),
    path("client/<int:pk>/update/", ClientUpdateView.as_view(), name="client_update"),
    path("client/<int:pk>/delete/", ClientDeleteView.as_view(), name="client_delete"),
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing/create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message/create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
]
