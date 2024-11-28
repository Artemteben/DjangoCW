from django.urls import path
from django.views.decorators.cache import cache_page

from blog.apps import BlogConfig

from . import views

app_name = BlogConfig.name

urlpatterns = [
    path('create/', views.BlogCreateView.as_view(), name='create'),
    path('update/<int:pk>/', views.BlogUpdateView.as_view(), name='update'),
    path('detail/<int:pk>/', views.BlogDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', views.BlogDeleteView.as_view(), name='delete'),
    path('list/', cache_page(60)(views.BlogListView.as_view()), name='list'),
]
