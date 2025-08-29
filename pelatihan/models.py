import uuid, os
from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Profile

NAMA_DOKUMEN_CHOICES = [
        ('00', 'Daftar Riwayat Hidup Peserta'),
        ('01', 'Nominatif Peserta'),
        ('02', 'Daftar Hadir Peserta'),
        ('03', 'Daftar Hadir Instruktur'),
        ('04', 'Jadwal Pelatihan'),
        ('05', 'Daftar Jam Mengajar Instruktur'),
        ('06', 'Daftar Nilai Akhir'),
        ('07', 'Tanda Terima ATK Peserta + ID Card'),
        ('08', 'Tanda Terima Pakaian Kerja/Kaos Olahraga+Training'),
        ('09', 'Tanda Terima Sepatu Kerja'),
        ('10', 'Tanda Terima Modul'),
        ('11', 'Tanda Terima Bahan Pelatihan'),
        ('12', 'Tanda Terima Konsumsi'),
        ('13', 'Fotocopy Sertifikat Pelatihan'),
        ('14', 'Dokumentasi Kegiatan'),
    ]

def get_list_nama_dokumen():
    return [code for code, _ in NAMA_DOKUMEN_CHOICES]

class Pelatihan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
    
    def persentase_progress(self):
        uploaded = self.dokumen.filter(status=STATUS_DOKUMEN_TERVERIFIKASI).count()
        total = len(NAMA_DOKUMEN_CHOICES)
        return int((uploaded / total) * 100)
    
    def __str__(self):
        return f"{self.judul} - {self.pic}"



def upload_to_dokumen(instance, filename):
    id_pelatihan = instance.pelatihan.id
    extension = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{extension}"
    return f'dokumen/{id_pelatihan}/{new_filename}'

STATUS_DOKUMEN_KOSONG = '0'
STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI = '1'
STATUS_DOKUMEN_PERLU_REVISI = '2'
STATUS_DOKUMEN_TERVERIFIKASI = '3'

STATUS_DOKUMEN_CHOICES = [
        (STATUS_DOKUMEN_KOSONG, 'Kosong'),
        (STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI, 'Dalam Proses Verifikasi'),
        (STATUS_DOKUMEN_PERLU_REVISI, 'Perlu Revisi'),
        (STATUS_DOKUMEN_TERVERIFIKASI, 'Terverifikasi'),
]

VERIFIKASI_CHOICES = [
        (STATUS_DOKUMEN_PERLU_REVISI, 'Perlu Revisi'),
        (STATUS_DOKUMEN_TERVERIFIKASI, 'Terverifikasi'),
]

class PelatihanDokumen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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

    class Meta:
        unique_together = ('pelatihan', 'nama')
    
    def __str__(self):
        label =  dict(NAMA_DOKUMEN_CHOICES).get(self.nama)
        return f"{self.nama} {label} - {self.pelatihan.judul}"

