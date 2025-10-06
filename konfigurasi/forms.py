# konfigurasi/forms.py
from django import forms
from .models import TahunAnggaran

class TahunAnggaranForm(forms.ModelForm):
    class Meta:
        model = TahunAnggaran
        # Add 'status' to the fields list
        fields = ['tahun', 'status', 'keterangan']
        widgets = {
            'tahun': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 2025'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan untuk tahun anggaran ini (opsional)'
            }),
            # Use RadioSelect for a clear choice
            'status': forms.RadioSelect,
        }