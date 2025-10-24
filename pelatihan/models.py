import os, shortuuid
from shortuuid.django_fields import ShortUUIDField

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from konfigurasi.models import StatusDokumen, Kejuruan, TahunAnggaran

User = get_user_model()
class Pelatihan(models.Model):
    class JenisPelatihan(models.TextChoices):
        BOARDING = 'BOARDING', 'Boarding'
        NON_BOARDING = 'NON_BOARDING', 'Non-Boarding'

    class MetodePelatihan(models.TextChoices):
        INSTITUTIONAL = 'INSTITUTIONAL', 'Institutional'
        MTU = 'MTU', 'MTU'
   

    # --- Isian Awal ---
    id = ShortUUIDField(primary_key=True, length=22, max_length=22)
    kejuruan = models.ForeignKey(Kejuruan, on_delete=models.PROTECT, related_name='pelatihan')
    judul = models.CharField(max_length=255, verbose_name="Program Pelatihan")
    paket_ke = models.PositiveSmallIntegerField(verbose_name="Paket Ke-")
    penyelenggara = models.ForeignKey(
        User,
        verbose_name="Penyelenggara (PIC)",
        on_delete=models.PROTECT,
        related_name='pelatihan'
    )
    tanggal_mulai_rencana = models.DateField(verbose_name="Tanggal Mulai (Rencana)")
    tanggal_selesai_rencana = models.DateField(verbose_name="Tanggal Selesai (Rencana)")
    tahun_anggaran = models.ForeignKey(TahunAnggaran, on_delete=models.PROTECT, related_name='pelatihan')

    # --- Detail Pelaksanaan ---
    jenis_pelatihan = models.CharField(max_length=15, choices=JenisPelatihan.choices, verbose_name="Jenis Pelatihan", blank=True)
    metode = models.CharField(max_length=15, choices=MetodePelatihan.choices, verbose_name="Metode Pelatihan", blank=True)
    tempat_pelaksanaan = models.CharField(max_length=255, blank=True)
    tanggal_mulai_aktual = models.DateField(verbose_name="Tanggal Mulai (Aktual)", null=True)
    tanggal_selesai_aktual = models.DateField(verbose_name="Tanggal Selesai (Aktual)", null=True)
    durasi_jp = models.PositiveSmallIntegerField(verbose_name="Durasi Pelatihan (JP)", null=True, blank=True)
    jam_per_hari = models.PositiveSmallIntegerField(verbose_name="Jam Pelajaran per Hari", default=8)
    waktu_pelatihan = models.CharField(
        max_length=100, 
        verbose_name="Waktu Pelaksanaan", 
        help_text="Contoh: 08:00 s.d. 16:00", 
        blank=True
    )

    # --- Administrasi ---
    no_sk = models.CharField(max_length=255, verbose_name="No. SK Penyelenggaraan", blank=True)
    tanggal_sk = models.DateField(verbose_name="Tgl. SK Penyelenggaraan", null=True, blank=True)
    tentang_sk = models.TextField(verbose_name="Tentang SK", blank=True)
    
    # --- Penandatangan Laporan ---
    jabatan_penandatangan = models.CharField(max_length=255, verbose_name="Nama Jabatan Ttd. Lap", blank=True)
    nama_penandatangan = models.CharField(max_length=255, verbose_name="Nama Pejabat Ttd. Lap", blank=True)
    nip_penandatangan = models.CharField(max_length=50, verbose_name="NIP Pejabat Ttd. Lap", blank=True)
    tanggal_penandatangan = models.DateField(verbose_name="Tgl. Ttd Lap", null=True, blank=True)

    # --- Statistik Peserta (diisi setelah pelatihan selesai) ---
    jumlah_peserta_laki = models.PositiveSmallIntegerField(verbose_name="Jumlah Peserta Laki-Laki", null=True, blank=True)
    jumlah_peserta_perempuan = models.PositiveSmallIntegerField(verbose_name="Jumlah Peserta Perempuan", null=True, blank=True)
    jumlah_lulus = models.PositiveSmallIntegerField(verbose_name="Jumlah Lulus", null=True, blank=True)
    jumlah_belum_lulus = models.PositiveSmallIntegerField(verbose_name="Jumlah Belum Lulus", null=True, blank=True)
    alasan_belum_lulus = models.TextField(blank=True)
    rata_rata_pendidikan = models.CharField(
        max_length=100,
        verbose_name="Rata-Rata Pendidikan Peserta",
        help_text="Contoh: SMA",
        blank=True
    )
    rata_rata_usia = models.FloatField(
        verbose_name="Rata-Rata Usia Peserta",
        help_text="Contoh: 25.3",
        null=True,
        blank=True
    )
    rata_rata_domisili = models.CharField(
        max_length=255,
        verbose_name="Rata-Rata Domisili Peserta",
        help_text="Contoh: Bekasi",
        blank=True
    )
    # --- Keterangan Tambahan ---
    keterangan_lanjutan = models.TextField(verbose_name="Ket. Lanjutan", blank=True)

    @property
    def rata_rata_gender_display(self):
        laki = self.jumlah_peserta_laki
        perempuan = self.jumlah_peserta_perempuan

        if laki > perempuan:
            return "Laki-laki"
        elif perempuan > laki:
            return "Perempuan"
        elif laki == perempuan:
            return "Seimbang"

    # def clean(self):
    #     super().clean()
    #     if self.tanggal_selesai and self.tanggal_mulai and self.tanggal_selesai < self.tanggal_mulai:
    #         raise ValidationError("Tanggal selesai harus setelah tanggal mulai")

    def persentase_progress(self):
        total = self.dokumen.count()
        if total == 0:
            return 0
        
        # Use the new TextChoices class for clarity
        uploaded = self.dokumen.filter(status=StatusDokumen.TERVERIFIKASI).count()
        return int((uploaded / total) * 100)

    def __str__(self):
        return f"{self.judul} - {self.paket_ke}"

class Instruktur(models.Model):
    """
    Menyimpan data master untuk Instruktur.
    """
    id = ShortUUIDField(primary_key=True, length=22, max_length=22)
    nama = models.CharField(max_length=255, verbose_name="Nama Lengkap Instruktur")
    
    class Meta:
        verbose_name = "Instruktur"
        verbose_name_plural = "Daftar Instruktur"
        ordering = ['nama']

    def __str__(self):
        return self.nama

class PelatihanInstruktur(models.Model):
    """
    Intermediary model to link multiple instructors and their subjects to a single Pelatihan.
    """
    id = ShortUUIDField(primary_key=True, length=22, max_length=22)
    pelatihan = models.ForeignKey('Pelatihan', on_delete=models.CASCADE, related_name='instruktur_set')
    
    instruktur = models.ForeignKey(
        Instruktur,
        on_delete=models.PROTECT, 
        related_name='materi_diajar'
    )
    
    materi = models.TextField(verbose_name="Materi yang Diajarkan")

    class Meta:
        verbose_name = "Instruktur Pelatihan"
        verbose_name_plural = "Daftar Instruktur Pelatihan"
        unique_together = ('pelatihan', 'instruktur', 'materi')

    def __str__(self):
        return f"{self.instruktur.nama} - {self.pelatihan.judul}"



def upload_to_dokumen(instance, filename):
    """
    Creates a more readable and unique filename.
    Example: dokumen/pelatihan-uuid/daftar-hadir-peserta-uuid.pdf
    """
    id_pelatihan = instance.pelatihan.id
    extension = os.path.splitext(filename)[1]
    # Use the human-readable name for better debugging
    doc_name_slug = slugify(instance.get_nama_display())
    new_filename = f"{doc_name_slug}-{shortuuid.uuid()}{extension}"
    return f'dokumen/{id_pelatihan}/{new_filename}'

class PelatihanLampiran(models.Model):
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

    id = ShortUUIDField(primary_key=True, length=22, max_length=22)
    pelatihan = models.ForeignKey(Pelatihan, on_delete=models.CASCADE,
                                  related_name='dokumen')

    nama = models.CharField(
        max_length=2,
        choices=DocumentName.choices,
        verbose_name="Jenis Dokumen",
    )

    status = models.ForeignKey(
        StatusDokumen,
        on_delete=models.PROTECT,
        verbose_name="Status Dokumen",
        default=StatusDokumen.KOSONG
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
        
    @property
    def is_kosong(self):
        return self.status_id == StatusDokumen.KOSONG

    @property
    def is_dalam_proses_verifikasi(self):
        return self.status_id == StatusDokumen.DALAM_PROSES_VERIFIKASI

    @property
    def is_perlu_revisi(self):
        return self.status_id == StatusDokumen.PERLU_REVISI

    @property
    def is_terverifikasi(self):
        return self.status_id == StatusDokumen.TERVERIFIKASI

    def __str__(self):
        # 2. USE get_FOO_display()
        return f"{self.get_nama_display()} - {self.pelatihan.judul}"