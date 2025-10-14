from django.urls import path
from . import views

app_name = 'konfigurasi'

urlpatterns = [
    path('tahun-anggaran/', views.manage_tahun_anggaran, name='manage_tahun_anggaran'),
    path('tahun-anggaran/<int:tahun_id>/edit/', views.edit_tahun_anggaran, name='edit_tahun_anggaran'),
    path('tahun-anggaran/<int:tahun_id>/delete/', views.delete_tahun_anggaran, name='delete_tahun_anggaran'),
]