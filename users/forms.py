from django.contrib.auth.forms import (AuthenticationForm, PasswordChangeForm,
                                       UserCreationForm)
from django.forms import ModelForm

from newsletter.forms import StyleFormMixin
from users.models import User


class LoginUserForm(StyleFormMixin, AuthenticationForm):
    """
    Модель формы для входа в профиль.
    """
    class Meta:
        model = User
        fields = '__all__'


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """
    Модель формы для регистрации пользователя.
    """
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')


class UserProfileForm(StyleFormMixin, ModelForm):
    """
    Модель формы для редактирования профиля.
    """
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name')


class UserPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    """
    Модель формы для изменения пароля пользователя.
    """
    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


class UserModerProfileForm(StyleFormMixin, ModelForm):
    """
    Модель формы для изменения профиля модератором.
    """
    class Meta:
        model = User
        fields = ('is_active',)
