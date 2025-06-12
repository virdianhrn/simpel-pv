from django.urls import path
from . import views

urlpatterns = [
    path("<int:pelatihan_id>", views.detail, name="detail"),
    path("<int:pelatihan_id>/edit", views.edit, name="edit"),
    path("<int:pelatihan_id>/skip/<int:document_id>", views.skip_document, name="skip_document"),
]