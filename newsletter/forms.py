from django.forms import BooleanField, ModelForm
from django import forms
from newsletter.models import Client, Message, Mailing


class StyleFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class MessageForm(StyleFormMixin, ModelForm):

    class Meta:
        model = Message
        exclude = ("author",)


class ClientForm(StyleFormMixin, ModelForm):

    class Meta:
        model = Client
        exclude = ("author",)


class CreateMailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Извлекаем пользователя
        super().__init__(*args, **kwargs)
        if user:
            # Фильтруем клиентов, принадлежащих текущему пользователю
            self.fields['clients'].queryset = Client.objects.filter(author=user)

class UpdateMailingForm(StyleFormMixin, ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["clients"].queryset = Client.objects.filter(author=user)
        self.fields["message"].queryset = Message.objects.filter(author=user)

    class Meta:
        model = Mailing
        exclude = ("author", "date_time")


class UpdateModerMailingForm(StyleFormMixin, ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        user.save()
        super().__init__(*args, **kwargs)

    class Meta:
        model = Mailing
        fields = ("status",)
