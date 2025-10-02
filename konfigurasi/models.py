from django.db import models

class TahunAnggaran(models.Model):
    class StatusChoices(models.TextChoices):
        AKTIF = 'AKTIF', 'Aktif'
        DITUTUP = 'DITUTUP', 'Ditutup'

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