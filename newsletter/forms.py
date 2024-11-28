from django.forms import BooleanField, ModelForm

from newsletter.models import Client, Message, Mailing


class StyleFormMixin:
    """
    Базовый класс миксин для всех форм.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class MessageForm(StyleFormMixin, ModelForm):
    """
    Модель формы для сообщений.
    """
    class Meta:
        model = Message
        exclude = ('author',)


class ClientForm(StyleFormMixin, ModelForm):
    """
    Модель формы для клиентов.
    """
    class Meta:
        model = Client
        exclude = ('author',)


class CreateMailingForm(StyleFormMixin, ModelForm):
    """
    Модель формы создания рассылок.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['clients'].queryset = Client.objects.filter(author=user)
        self.fields['message'].queryset = Message.objects.filter(author=user)

    class Meta:
        model = Mailing
        exclude = ('author', 'status', 'date_time')


class UpdateMailingForm(StyleFormMixin, ModelForm):
    """
    Модель формы редактирования рассылок.
    """
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['clients'].queryset = Client.objects.filter(author=user)
        self.fields['message'].queryset = Message.objects.filter(author=user)

    class Meta:
        model = Mailing
        exclude = ('author', 'date_time')


class UpdateModerMailingForm(StyleFormMixin, ModelForm):
    """
    Модель формы для редактирования модератором.
    """

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        user.save()
        super().__init__(*args, **kwargs)

    class Meta:
        model = Mailing
        fields = ('status',)
