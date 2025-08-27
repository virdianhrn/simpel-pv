from django.urls import path
from . import views

urlpatterns = [
    path("<int:pelatihan_id>", views.PelatihanDetailView.as_view(), name="detail"),
    path("<int:pelatihan_id>/edit", views.edit, name="edit"),
    path("<int:pelatihan_id>/skip/<int:document_id>", views.skip_document, name="skip_document"),
    path("<int:pelatihan_id>/download", views.download_merged_docs, name="download_merged_docs"),
    path("<int:pelatihan_id>/verifikasi/<int:document_id>", views.verifikasi_dokumen, name="verifikasi_dokumen"),
]