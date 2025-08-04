from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pelatihan, PelatihanDokumen
from .models import STATUS_DOKUMEN_KOSONG, STATUS_DOKUMEN_SEDANG_VERIFIKASI, STATUS_DOKUMEN_PERLU_REVISI, STATUS_DOKUMEN_TERVERIFIKASI
from .forms import PenambahanDokumenFormSet, PelatihanForm
from django.core.files.base import ContentFile
from io import BytesIO
from PyPDF2 import PdfWriter

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
        'formset': formset,
        'STATUS_DOKUMEN_KOSONG': STATUS_DOKUMEN_KOSONG,
        'STATUS_DOKUMEN_SEDANG_VERIFIKASI': STATUS_DOKUMEN_SEDANG_VERIFIKASI,
        'STATUS_DOKUMEN_PERLU_REVISI': STATUS_DOKUMEN_PERLU_REVISI,
        'STATUS_DOKUMEN_TERVERIFIKASI': STATUS_DOKUMEN_TERVERIFIKASI,
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
        buffer = BytesIO()
        writer = PdfWriter()

        writer.add_blank_page(width=595, height=842) # A4 size in points
        writer.write(buffer)
        buffer.seek(0)

        document.status = STATUS_DOKUMEN_SEDANG_VERIFIKASI
        document.file_url.save('blank.pdf', ContentFile(buffer.read()))
        
        buffer.close()
        document.save()
        return redirect('detail', pelatihan_id=pelatihan.id)

    return redirect('detail', pelatihan_id=pelatihan.id)