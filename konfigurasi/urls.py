from django.urls import path
from . import views

app_name = 'konfigurasi'

urlpatterns = [
    path('tahun-anggaran/', views.manage_tahun_anggaran, name='manage_tahun_anggaran'),
]