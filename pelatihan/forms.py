from .models import Pelatihan, Instruktur, PelatihanLampiran, PelatihanInstruktur
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from konfigurasi.models import StatusDokumen, Role

User = get_user_model()
verification_queryset = StatusDokumen.objects.filter(
    pk__in=[
        StatusDokumen.PERLU_REVISI,
        StatusDokumen.TERVERIFIKASI
    ]
)

class PelatihanForm(forms.ModelForm):
    penyelenggara = forms.ModelChoiceField(
        queryset=User.objects.filter(role__id=Role.PENYELENGGARA).order_by('first_name'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="PIC Penyelenggara"
    )

    class Meta:
        model = Pelatihan
        fields = [
            'judul', 'kejuruan', 'jenis_pelatihan', 'penyelenggara', 'metode',
            'tempat_pelaksanaan', 'tanggal_mulai_rencana', 'tanggal_selesai_rencana',
            'tanggal_mulai_aktual', 'tanggal_selesai_aktual', 'durasi_jp',
            'jam_per_hari', 'waktu_pelatihan', 'tahun_anggaran', 'paket_ke',
            'no_sk', 'tanggal_sk', 'tentang_sk', 'jabatan_penandatangan',
            'nama_penandatangan', 'nip_penandatangan', 'tanggal_penandatangan',
            'jumlah_peserta_laki', 'jumlah_peserta_perempuan', 'jumlah_lulus',
            'jumlah_belum_lulus', 'alasan_belum_lulus', 'rata_rata_pendidikan',
            'rata_rata_usia', 'rata_rata_domisili', 'keterangan_lanjutan'
        ]
        
        # Menambahkan widget untuk semua field agar sesuai dengan gaya Bootstrap
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control'}),
            'kejuruan': forms.Select(attrs={'class': 'form-select'}),
            'jenis_pelatihan': forms.Select(attrs={'class': 'form-select'}),
            'metode': forms.Select(attrs={'class': 'form-select'}),
            'tempat_pelaksanaan': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_mulai_rencana': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai_rencana': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_mulai_aktual': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai_aktual': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'durasi_jp': forms.NumberInput(attrs={'class': 'form-control'}),
            'jam_per_hari': forms.NumberInput(attrs={'class': 'form-control'}),
            'waktu_pelatihan': forms.TextInput(attrs={'class': 'form-control'}),
            'tahun_anggaran': forms.Select(attrs={'class': 'form-select'}),
            'paket_ke': forms.NumberInput(attrs={'class': 'form-control'}),
            'no_sk': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_sk': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tentang_sk': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'jabatan_penandatangan': forms.TextInput(attrs={'class': 'form-control'}),
            'nama_penandatangan': forms.TextInput(attrs={'class': 'form-control'}),
            'nip_penandatangan': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_penandatangan': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'jumlah_peserta_laki': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_peserta_perempuan': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_lulus': forms.NumberInput(attrs={'class': 'form-control'}),
            'jumlah_belum_lulus': forms.NumberInput(attrs={'class': 'form-control'}),
            'alasan_belum_lulus': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rata_rata_pendidikan': forms.TextInput(attrs={'class': 'form-control'}),
            'rata_rata_usia': forms.NumberInput(attrs={'class': 'form-control'}),
            'rata_rata_domisili': forms.TextInput(attrs={'class': 'form-control'}),
            'keterangan_lanjutan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        admin_only_fields = [
            'judul', 'kejuruan', 'penyelenggara', 'tahun_anggaran', 'paket_ke',
            'tanggal_mulai_rencana', 'tanggal_selesai_rencana'
        ]

        # Kasus 1: Admin membuat Pelatihan BARU
        if self.user and self.user.is_admin and self.instance._state.adding:
            fields_to_show = admin_only_fields
            all_fields = list(self.fields.keys())
            for field_name in all_fields:
                if field_name not in fields_to_show:
                    self.fields.pop(field_name) # Hapus field lain dari formulir
        
        # Kasus 2: Penyelenggara mengedit Pelatihan
        elif self.user and not self.user.is_admin and self.instance.pk:
            for field_name in admin_only_fields:
                if field_name in self.fields:
                    self.fields[field_name].disabled = True
        
        # Kasus 3: Admin mengedit Pelatihan
        # Tidak perlu melakukan apa-apa, formulir akan tampil lengkap dan bisa diedit


class PelatihanInstrukturForm(forms.ModelForm):
    """Form ini digunakan di dalam formset untuk menata field instruktur."""
    instruktur = forms.ModelChoiceField(
        queryset=Instruktur.objects.all().order_by('nama'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Nama Instruktur"
    )

    class Meta:
        model = PelatihanInstruktur
        fields = ['instruktur', 'materi']
        widgets = {
            'materi': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }

InstrukturFormSet = forms.inlineformset_factory(
    parent_model=Pelatihan,
    model=PelatihanInstruktur,
    form=PelatihanInstrukturForm,
    extra=0,
    can_delete=True,
)

class LampiranForm(forms.ModelForm):
    class Meta:
        model = PelatihanLampiran
        fields = ['file_url']
        widgets = {
            'file_url': forms.FileInput(attrs={
                'style': 'display:none;',
                'onchange': 'this.form.submit();',
                'accept': '.pdf'
            }),
        }
    def clean_file_url(self):
        """Custom validation to ensure the uploaded file is less than 5MB."""
        file = self.cleaned_data.get('file_url', False)
        
        if file:
            # Define the maximum size in bytes (5MB)
            max_size = 5 * 1024 * 1024
            
            if file.size > max_size:
                raise ValidationError(
                    f'Ukuran file tidak boleh melebihi 5 MB.'
                )
                
        return file

LampiranFormSet = forms.inlineformset_factory(
    parent_model=Pelatihan,
    model=PelatihanLampiran,
    form=LampiranForm,
    extra=0,
    can_delete=False,
)

class VerifikasiLampiranForm(forms.ModelForm):
    status = forms.ModelChoiceField(
        queryset = verification_queryset,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Status Verifikasi",
        empty_label=None
    )
    notes = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    class Meta:
        model = PelatihanLampiran
        fields = ['status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].label = format_html(
            'Notes <span class="text-danger">*</span>', 
        )