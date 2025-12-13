from django.urls import path
from . import views

app_name = 'translator'

urlpatterns = [
    path('', views.TranslatorView.as_view(), name='translate'),
    path('api/', views.TranslateAPIView.as_view(), name='api'),
    path('share/<slug:slug>/', views.ShareView.as_view(), name='share'),
]
