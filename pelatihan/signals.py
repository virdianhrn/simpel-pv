from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pelatihan, PelatihanDokumen, get_list_nama_dokumen

@receiver(post_save, sender=Pelatihan)
def create_pelatihan_dokumen(sender, instance, created, **kwargs):
    if created:
        list_nama_dokumen = get_list_nama_dokumen()
        for i in list_nama_dokumen:
            PelatihanDokumen.objects.create(pelatihan=instance, nama=i)
