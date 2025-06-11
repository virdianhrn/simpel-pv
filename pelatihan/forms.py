from .models import Pelatihan, PelatihanDokumen
from .models import NAMA_DOKUMEN_CHOICES, STATUS_DOKUMEN_CHOICES
from django import forms

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
                'onchange': 'this.form.submit();'
            }),
        }

PenambahanDokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanDokumen,
    form=PenambahanDokumenForm,
    extra=0,
    can_delete=False,
)