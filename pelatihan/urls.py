from django.urls import path
from . import views

app_name = 'pelatihan'

urlpatterns = [
    path('add', views.add, name='add'),
    path("<str:pelatihan_id>/edit", views.edit, name="edit"),
    path("<str:pelatihan_id>/delete", views.delete, name="delete"),
    path("<str:pelatihan_id>/download", views.download_merged_docs, name="download_merged_docs"),
    path("<str:pelatihan_id>/skip/<str:document_id>", views.skip_document, name="skip_document"),
    path("<str:pelatihan_id>/verifikasi/<str:document_id>", views.verifikasi_dokumen, name="verifikasi_dokumen"),
    path("<str:pelatihan_id>", views.DetailView.as_view(), name="detail"),
]