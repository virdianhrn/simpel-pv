# konfigurasi/forms.py
from django import forms
from .models import TahunAnggaran

class TahunAnggaranForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=TahunAnggaran.StatusChoices.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = TahunAnggaran
        fields = ['tahun', 'status', 'target', 'keterangan']
        widgets = {
            'tahun': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 2025'
            }),
            'target': forms.NumberInput(attrs={
                'class': 'form-control',
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Catatan untuk tahun anggaran ini (opsional)'
            }),
        }

    def clean_tahun(self):
        """
        Custom validation to check if the 'tahun' already exists.
        """
        tahun = self.cleaned_data.get('tahun')
        
        # self.instance.pk will be None when creating a new object.
        # We check if a year exists, excluding the current instance if we are editing.
        if TahunAnggaran.objects.filter(tahun=tahun).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Tahun Anggaran ini sudah ada di dalam sistem.")
            
        return tahun