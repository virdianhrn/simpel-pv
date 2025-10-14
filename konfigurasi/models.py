from django.db import models

class TahunAnggaran(models.Model):
    class StatusChoices(models.TextChoices):
        AKTIF = 'AKTIF', 'Aktif'
        DITUTUP = 'DITUTUP', 'Ditutup'
        DIARSIPKAN = 'DIARSIPKAN', 'Diarsipkan'

    tahun = models.PositiveIntegerField(
        primary_key=True, # The year itself is the best primary key
        unique=True,
        help_text="Tahun anggaran, contoh: 2025"
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.AKTIF,
        help_text="Status tahun anggaran (hanya pelatihan dengan tahun berstatus 'Aktif' yang bisa dibuat)"
    )

    target = models.PositiveIntegerField(
        default=0,
        verbose_name="Target Paket Pelatihan",
        help_text="Jumlah target paket pelatihan untuk tahun anggaran ini."
    )
    
    keterangan = models.TextField(
        blank=True,
        null=True,
        help_text="Catatan atau keterangan tambahan untuk tahun anggaran ini"
    )

    class Meta:
        verbose_name = "Tahun Anggaran"
        verbose_name_plural = "Daftar Tahun Anggaran"
        ordering = ['-tahun'] # Show the most recent year first

    def __str__(self):
        return str(self.tahun)

class Role(models.Model):
    ADMIN = 'AD'
    PENYELENGGARA = 'PL'

    id = models.CharField(primary_key=True, max_length=2, help_text="Contoh: AD, PL")
    nama = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nama

    @classmethod
    def get_choices(cls):
        """
        Queries the database and returns all roles in the format
        expected by a form's 'choices' attribute.
        Example: (('AD', 'Admin'), ('PL', 'Penyelenggara'))
        """
        return tuple((role.id, role.nama) for role in cls.objects.all())

class StatusDokumen(models.Model):
    # Define constants for the primary keys
    KOSONG = 1
    DALAM_PROSES_VERIFIKASI = 2
    PERLU_REVISI = 3
    TERVERIFIKASI = 4

    id = models.PositiveSmallIntegerField(primary_key=True)
    nama = models.CharField(max_length=50, unique=True)
    keterangan = models.TextField(blank=True, help_text="Deskripsi singkat mengenai status ini.")

    class Meta:
        verbose_name = "Status Dokumen"
        verbose_name_plural = "Daftar Status Dokumen"

    def __str__(self):
        return self.nama