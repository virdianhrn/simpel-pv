from django.urls import path

from . import views

urlpatterns = [
    path("<int:pelatihan_id>", views.detail, name="detail"),
]