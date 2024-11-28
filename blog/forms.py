from django.forms import ModelForm

from blog.models import Blog
from newsletter.forms import StyleFormMixin


class BlogCreateForm(StyleFormMixin, ModelForm):
    """
    Форма для создания блога.
    """
    class Meta:
        model = Blog
        exclude = ('views_count',)
