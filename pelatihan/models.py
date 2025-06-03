import random
import string
from django.db import models
from accounts.models import Profile

class Pelatihan(models.Model):
    judul = models.CharField(max_length=255, verbose_name="Judul Pelatihan")
    pic = models.ForeignKey(Profile, verbose_name="PIC Pelatihan", on_delete=models.CASCADE)
    tanggal_mulai = models.DateField(verbose_name="Tanggal Mulai Pelatihan")
    tanggal_selesai = models.DateField(verbose_name="Tanggal Selesai Pelatihan")
    durasi = models.PositiveSmallIntegerField(verbose_name="Durasi Pelatihan") # Dalam JP

    def __str__(self):
        return f"{self.judul} - {self.pic}"

def upload_to_dokumen(instance, _):
    id_pelatihan = instance.pelatihan.id
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return f'media/dokumen/{id_pelatihan}/{instance.nama}{random_string}.pdf'

# NOTE: Setup MEDIA_ROOT
# NOTE: Change temporary name
class PelatihanDokumen(models.Model):
    NAMA_DOKUMEN_CHOICES = [
        ('01', '1-Dokumen1'),
        ('02', '2-Dokumen2'),
        ('03', '3-Dokumen3'),
        ('04', '4-Dokumen4'),
        ('05', '5-Dokumen5'),
        ('06', '6-Dokumen6'),
        ('07', '7-Dokumen7'),
        ('08', '8-Dokumen8'),
        ('09', '9-Dokumen9'),
        ('10', '10-Dokumen10'),
        ('11', '11-Dokumen11'),
        ('12', '12-Dokumen12'),
        ('13', '13-Dokumen13'),
        ('14', '14-Dokumen14'),
        ('15', '15-Dokumen15'),
    ]

    pelatihan = models.ForeignKey(Pelatihan, on_delete=models.CASCADE, related_name='dokumen')
    nama = models.CharField(
        max_length=2,
        choices=NAMA_DOKUMEN_CHOICES,
        verbose_name="Jenis Dokumen"
    )
    file = models.FileField(upload_to=upload_to_dokumen)
    
    def __str__(self):
        label = self.NAMA_DOKUMEN_CHOICES.get(self.nama)
        return f"{label} - {self.pelatihan.judul}"

