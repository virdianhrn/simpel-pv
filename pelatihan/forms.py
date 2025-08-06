from .models import Pelatihan, PelatihanDokumen, VERIFIKASI_CHOICES
from django import forms
from django.core.exceptions import ValidationError

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

PenambahanDokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanDokumen,
    form=PenambahanDokumenForm,
    extra=0,
    can_delete=False,
)

class VerifikasiDokumenForm(forms.ModelForm):
    class Meta:
        model = PelatihanDokumen
        fields = ['status', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the choices for the 'status' field
        self.fields['status'].choices = VERIFIKASI_CHOICES
        # ------------------------------------

        # This is your existing code to add CSS classes
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'notes':
                field.widget = forms.Textarea(attrs={'class': 'form-control', 'rows': 3})