from .models import Pelatihan, PelatihanDokumen
from .models import NAMA_DOKUMEN_CHOICES, STATUS_DOKUMEN_CHOICES
from django import forms

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
            'file_url': forms.FileInput(attrs={
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