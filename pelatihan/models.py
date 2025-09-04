import os
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from accounts.models import Profile


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
        total = self.dokumen.count()
        if total == 0:
            return 0
        
        # Use the new TextChoices class for clarity
        uploaded = self.dokumen.filter(status=PelatihanDokumen.DocumentStatus.TERVERIFIKASI).count()
        return int((uploaded / total) * 100)

    def __str__(self):
        return f"{self.judul} - {self.pic}"


def upload_to_dokumen(instance, filename):
    """
    Creates a more readable and unique filename.
    Example: dokumen/pelatihan-uuid/daftar-hadir-peserta-uuid.pdf
    """
    id_pelatihan = instance.pelatihan.id
    extension = os.path.splitext(filename)[1]
    # Use the human-readable name for better debugging
    doc_name_slug = slugify(instance.get_nama_display())
    new_filename = f"{doc_name_slug}-{uuid.uuid4()}{extension}"
    return f'dokumen/{id_pelatihan}/{new_filename}'


class PelatihanDokumen(models.Model):
    # 1. ENCAPSULATED CHOICES USING TextChoices
    class DocumentStatus(models.TextChoices):
        KOSONG = '0', 'Kosong'
        DALAM_PROSES_VERIFIKASI = '1', 'Dalam Proses Verifikasi'
        PERLU_REVISI = '2', 'Perlu Revisi'
        TERVERIFIKASI = '3', 'Terverifikasi'

    class DocumentName(models.TextChoices):
        DRH_PESERTA = '00', 'Daftar Riwayat Hidup Peserta'
        NOMINATIF_PESERTA = '01', 'Nominatif Peserta'
        DAFTAR_HADIR_PESERTA = '02', 'Daftar Hadir Peserta'
        DAFTAR_HADIR_INSTRUKTUR = '03', 'Daftar Hadir Instruktur'
        JADWAL_PELATIHAN = '04', 'Jadwal Pelatihan'
        JAM_MENGAJAR_INSTRUKTUR = '05', 'Daftar Jam Mengajar Instruktur'
        NILAI_AKHIR = '06', 'Daftar Nilai Akhir'
        TERIMA_ATK = '07', 'Tanda Terima ATK Peserta + ID Card'
        TERIMA_PAKAIAN = '08', 'Tanda Terima Pakaian Kerja/Kaos Olahraga+Training'
        TERIMA_SEPATU = '09', 'Tanda Terima Sepatu Kerja'
        TERIMA_MODUL = '10', 'Tanda Terima Modul'
        TERIMA_BAHAN = '11', 'Tanda Terima Bahan Pelatihan'
        TERIMA_KONSUMSI = '12', 'Tanda Terima Konsumsi'
        FOTOCOPY_SERTIFIKAT = '13', 'Fotocopy Sertifikat Pelatihan'
        DOKUMENTASI = '14', 'Dokumentasi Kegiatan'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pelatihan = models.ForeignKey(Pelatihan, on_delete=models.CASCADE,
                                  related_name='dokumen')

    nama = models.CharField(
        max_length=2,
        choices=DocumentName.choices,
        verbose_name="Jenis Dokumen",
    )

    status = models.CharField(
        max_length=1,
        choices=DocumentStatus.choices,
        verbose_name="Status Dokumen",
        default=DocumentStatus.KOSONG
    )

    file_url = models.FileField(
        upload_to=upload_to_dokumen,
        verbose_name="URL Dokumen",
        blank=True,
        null=True # Good practice for optional FileFields
    )

    notes = models.CharField(
        max_length=255,
        verbose_name="Notes Admin",
        blank=True
    )

    class Meta:
        unique_together = ('pelatihan', 'nama')

    @classmethod
    def get_all_document_codes(cls):
        return cls.DocumentName.values
        
    def __str__(self):
        # 2. USE get_FOO_display()
        return f"{self.get_nama_display()} - {self.pelatihan.judul}"