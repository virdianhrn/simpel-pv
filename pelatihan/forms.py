from .models import Pelatihan, PelatihanLampiran
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
    # Explicitly define the 'pic' field
    pic = forms.ModelChoiceField(
        queryset=User.objects.filter(role__id=Role.PENYELENGGARA).order_by('first_name'),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="PIC Penyelenggara"
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and not self.user.is_admin:
            if 'pic' in self.fields:
                del self.fields['pic']

    class Meta:
        model = Pelatihan
        fields = ['judul', 'pic', 'tanggal_mulai', 'tanggal_selesai', 'durasi']
        widgets = {
            'judul': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_selesai': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'durasi': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'durasi': 'Durasi (JP)',
        }

class DokumenForm(forms.ModelForm):
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

DokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanLampiran,
    form=DokumenForm,
    extra=0,
    can_delete=False,
)

class VerifikasiDokumenForm(forms.ModelForm):
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