from .models import Pelatihan, PelatihanDokumen
from django import forms

class PelatihanDokumenForm(forms.ModelForm):
    class Meta:
        model = PelatihanDokumen
        fields = ['nama', 'file_url', 'status']
        widgets = {
            'nama': forms.TextInput(attrs={'readonly': 'readonly'}),
            'file_url': forms.ClearableFileInput(attrs={
                'onchange': 'this.form.submit();'
            }),
            'status': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].disabled = True

PelatihanDokumenFormSet = forms.inlineformset_factory(
    Pelatihan,
    PelatihanDokumen,
    form=PelatihanDokumenForm,
    extra=0,
    can_delete=False,
)