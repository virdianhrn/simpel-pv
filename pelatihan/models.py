import random
import string
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Profile

# NOTE: Change temporary name
NAMA_DOKUMEN_CHOICES = [
        ('00', 'DokumenO'),
        ('01', 'DokumenN'),
        ('02', 'DokumenM'),
        ('03', 'DokumenL'),
        ('04', 'DokumenK'),
        ('05', 'DokumenJ'),
        ('06', 'DokumenI'),
        ('07', 'DokumenH'),
        ('08', 'DokumenG'),
        ('09', 'DokumenF'),
        ('10', 'DokumenE'),
        ('11', 'DokumenD'),
        ('12', 'DokumenC'),
        ('13', 'DokumenB'),
        ('14', 'DokumenA'),
    ]

def get_list_nama_dokumen():
    return [code for code, _ in NAMA_DOKUMEN_CHOICES]

class Pelatihan(models.Model):
    judul = models.CharField(max_length=255, verbose_name="Judul Pelatihan")
    pic = models.ForeignKey(Profile, verbose_name="PIC Pelatihan", 
                            on_delete=models.CASCADE, related_name='pelatihan')
    tanggal_mulai = models.DateField(verbose_name="Tanggal Mulai Pelatihan")
    tanggal_selesai = models.DateField(verbose_name="Tanggal Selesai Pelatihan")
    durasi = models.PositiveSmallIntegerField(verbose_name="Durasi Pelatihan") # Dalam JP

    def clean(self):
        super().clean()
        if self.tanggal_selesai and self.tanggal_mulai and self.tanggal_selesai < self.tanggal_mulai:
            raise ValidationError("Tanggal selesai harus setelah tanggal mulai")
    
    #NOTE: No hard code please 
    def persentase_progress(self):
        uploaded = self.dokumen.filter(status='3').count()
        total = len(NAMA_DOKUMEN_CHOICES)
        return int((uploaded / total) * 100)
    
    def __str__(self):
        return f"{self.judul} - {self.pic}"



def upload_to_dokumen(instance, _):
    id_pelatihan = instance.pelatihan.id
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    return f'dokumen/{id_pelatihan}/{instance.nama}{random_string}.pdf'

STATUS_DOKUMEN_CHOICES = [
        ('0', 'Kosong'),
        ('1', 'Sedang Diverifikasi'),
        ('2', 'Perlu Revisi'),
        ('3', 'Terverifikasi'),
]

class PelatihanDokumen(models.Model):
    pelatihan = models.ForeignKey(Pelatihan, on_delete=models.CASCADE, 
                                  related_name='dokumen')
    
    nama = models.CharField(
        max_length=2,
        choices=NAMA_DOKUMEN_CHOICES,
        verbose_name="Jenis Dokumen",
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_DOKUMEN_CHOICES,
        verbose_name="Status Dokumen",
        default = '0'
    )

    file_url = models.FileField(
        upload_to=upload_to_dokumen, 
        verbose_name="URL Dokumen",
        blank=True
    )

    notes = models.CharField(
        max_length=255,
        verbose_name="Notes Admin",
        blank=True
    )
    
    def __str__(self):
        label =  dict(NAMA_DOKUMEN_CHOICES).get(self.nama)
        return f"{self.nama} {label} - {self.pelatihan.judul}"

