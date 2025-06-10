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
    nama = forms.ChoiceField(
        choices=NAMA_DOKUMEN_CHOICES,
        widget=forms.Select(attrs={'readonly': 'readonly'}),
    )

    status = forms.ChoiceField(
        choices=STATUS_DOKUMEN_CHOICES,
        widget=forms.Select(attrs={'readonly': 'readonly'}),
    )
    class Meta:
        model = PelatihanDokumen
        fields = ['nama', 'file_url', 'status', 'notes']
        widgets = {
            'file_url': forms.ClearableFileInput(attrs={
                'onchange': 'this.form.submit();'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nama'].disabled = True
        self.fields['status'].disabled = True
        self.fields['notes'].disabled = True

PenambahanDokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanDokumen,
    form=PenambahanDokumenForm,
    extra=0,
    can_delete=False,
)