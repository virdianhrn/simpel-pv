from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import STATUS_DOKUMEN_SEDANG_VERIFIKASI, Pelatihan, PelatihanDokumen
from .forms import PenambahanDokumenFormSet, PelatihanForm
from django.core.files.base import ContentFile

def detail(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    if request.method == 'POST':
        formset = PenambahanDokumenFormSet(request.POST, request.FILES, instance=pelatihan)
        if formset.is_valid():
            for form in formset:
                if 'file_url' in form.changed_data:
                    form.instance.status = STATUS_DOKUMEN_SEDANG_VERIFIKASI
            formset.save()
            return redirect('detail', pelatihan_id=pelatihan.id)
    else:
        formset = PenambahanDokumenFormSet(instance=pelatihan)
  
    context = {
        'pelatihan': pelatihan,
        'formset': formset
    }
    return render(request, 'detail_pelatihan.html', context)

def edit(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    if request.method == 'POST':
        form = PelatihanForm(request.POST, instance=pelatihan)
        if form.is_valid():
            form.save()
            return redirect('detail', pelatihan_id=pelatihan.id)
    else:
        form = PelatihanForm(instance=pelatihan)
  
    context = {
        'pelatihan': pelatihan,
        'form': form
    }
    return render(request, 'edit_pelatihan.html', context)

def skip_document(request, pelatihan_id, document_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)

    if request.method == 'POST':
        document = get_object_or_404(PelatihanDokumen, pk=document_id)
        with open(r'media\dokumen\blank.pdf', 'rb') as f:
            document.status = STATUS_DOKUMEN_SEDANG_VERIFIKASI
            document.file_url.save('blank.pdf', ContentFile(f.read()))

        document.save()
        return redirect('detail', pelatihan_id=pelatihan.id)

    return redirect('detail', pelatihan_id=pelatihan.id)