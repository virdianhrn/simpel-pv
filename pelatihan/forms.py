from .models import Pelatihan, PelatihanDokumen, VERIFIKASI_CHOICES
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
class PelatihanForm(forms.ModelForm):
    tanggal_mulai = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    tanggal_selesai = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    class Meta:
        model = Pelatihan
        fields = ['judul', 'tanggal_mulai', 'tanggal_selesai', 'durasi']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class PenambahanDokumenForm(forms.ModelForm):
    class Meta:
        model = PelatihanDokumen
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

PenambahanDokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanDokumen,
    form=PenambahanDokumenForm,
    extra=0,
    can_delete=False,
)

class VerifikasiDokumenForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices = VERIFIKASI_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'rows': 3})
    )
    notes = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    class Meta:
        model = PelatihanDokumen
        fields = ['status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].label = format_html(
            'Notes <span class="text-danger">*</span>', 
        )