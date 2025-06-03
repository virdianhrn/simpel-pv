import random
import string
from django.db import models
from accounts.models import Profile

NAMA_DOKUMEN_CHOICES = [
        ('01', 'DokumenO'),
        ('02', 'DokumenN'),
        ('03', 'DokumenM'),
        ('04', 'DokumenL'),
        ('05', 'DokumenK'),
        ('06', 'DokumenJ'),
        ('07', 'DokumenI'),
        ('08', 'DokumenH'),
        ('09', 'DokumenG'),
        ('10', 'DokumenF'),
        ('11', 'DokumenE'),
        ('12', 'DokumenD'),
        ('13', 'DokumenC'),
        ('14', 'DokumenB'),
        ('15', 'DokumenA'),
    ]

class Pelatihan(models.Model):
    judul = models.CharField(max_length=255, verbose_name="Judul Pelatihan")
    pic = models.ForeignKey(Profile, verbose_name="PIC Pelatihan", 
                            on_delete=models.CASCADE, related_name='pelatihan')
    tanggal_mulai = models.DateField(verbose_name="Tanggal Mulai Pelatihan")
    tanggal_selesai = models.DateField(verbose_name="Tanggal Selesai Pelatihan")
    durasi = models.PositiveSmallIntegerField(verbose_name="Durasi Pelatihan") # Dalam JP

    def persentase_progress(self):
        uploaded = self.dokumen.count()
        total = len(NAMA_DOKUMEN_CHOICES)
        return int((uploaded / total) * 100) if total > 0 else 0
    
    def __str__(self):
        return f"{self.judul} - {self.pic}"

def upload_to_dokumen(instance, _):
    id_pelatihan = instance.pelatihan.id
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f'media/dokumen/{id_pelatihan}/{instance.nama}{random_string}.pdf'


# NOTE: Setup MEDIA_ROOT
# NOTE: Change temporary name
class PelatihanDokumen(models.Model):
    pelatihan = models.ForeignKey(Pelatihan, on_delete=models.CASCADE, 
                                  related_name='dokumen')
    nama = models.CharField(
        max_length=2,
        choices=NAMA_DOKUMEN_CHOICES,
        verbose_name="Jenis Dokumen"
    )
    uploaded = models.FileField(upload_to=upload_to_dokumen, verbose_name="Dokumen yang Diupload")
    
    def __str__(self):
        label =  dict(NAMA_DOKUMEN_CHOICES).get(self.nama)
        return f"{label} - {self.pelatihan.judul}"

