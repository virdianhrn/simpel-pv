from django.urls import path
from . import views

app_name = 'evaluasi'

urlpatterns = [
    path('', views.dashboard_evaluasi, name='dashboard'),
]