from django.urls import path
from . import views

app_name = 'pelatihan'

urlpatterns = [
    path('add', views.add, name='add'),
    path("<uuid:pelatihan_id>", views.DetailView.as_view(), name="detail"),
    path("<uuid:pelatihan_id>/edit", views.edit, name="edit"),
    path("<uuid:pelatihan_id>/delete", views.delete, name="delete"),
    path("<uuid:pelatihan_id>/skip/<uuid:document_id>", views.skip_document, name="skip_document"),
    path("<uuid:pelatihan_id>/download", views.download_merged_docs, name="download_merged_docs"),
    path("<uuid:pelatihan_id>/verifikasi/<uuid:document_id>", views.verifikasi_dokumen, name="verifikasi_dokumen"),
]