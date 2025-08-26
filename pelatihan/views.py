from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pelatihan, PelatihanDokumen
from .models import STATUS_DOKUMEN_KOSONG, STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI, STATUS_DOKUMEN_PERLU_REVISI, STATUS_DOKUMEN_TERVERIFIKASI
from .forms import PenambahanDokumenFormSet, PelatihanForm, VerifikasiDokumenForm
from django.core.files.base import ContentFile
from io import BytesIO
from PyPDF2 import PdfWriter, PdfMerger, PdfReader
from django.contrib import messages
import json

def verifikasi_dokumen(request, pelatihan_id, document_id):
    document = get_object_or_404(PelatihanDokumen, pk=document_id)

    if request.method == 'POST':
        form = VerifikasiDokumenForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'status': document.get_status_display()})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = VerifikasiDokumenForm(instance=document)
    return render(request, 'form_verifikasi.html', {'form': form, 'document': document})

def detail_penyelengara(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    #TODO: File format dan size verification
    if request.method == 'POST':
        formset = PenambahanDokumenFormSet(request.POST, request.FILES, instance=pelatihan)
        if formset.is_valid():
            for form in formset:
                if 'file_url' in form.changed_data:
                    form.instance.status = STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI
            formset.save()
            messages.success(request, 'Dokumen berhasil diunggah!')
        
        else:
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
            return redirect('detail', pelatihan_id=pelatihan.id)
    else:
        formset = PenambahanDokumenFormSet(instance=pelatihan)
    
    message_list = []
    for message in messages.get_messages(request):
        message_list.append({
            'body': str(message),
            'tags': message.tags,
        })
    
    context = {
        'pelatihan': pelatihan,
        'formset': formset,
        'messages_json': json.dumps(message_list),
        'STATUS_DOKUMEN_KOSONG': STATUS_DOKUMEN_KOSONG,
        'STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI': STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI,
        'STATUS_DOKUMEN_PERLU_REVISI': STATUS_DOKUMEN_PERLU_REVISI,
        'STATUS_DOKUMEN_TERVERIFIKASI': STATUS_DOKUMEN_TERVERIFIKASI,
    }
    return render(request, 'detail_pelatihan.html', context)

def detail_admin(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    if request.method == 'POST':
        formset = PenambahanDokumenFormSet(request.POST, request.FILES, instance=pelatihan)
        if formset.is_valid():
            for form in formset:
                if 'file_url' in form.changed_data:
                    form.instance.status = STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI
            formset.save()
            return redirect('detail', pelatihan_id=pelatihan.id)
    else:
        formset = PenambahanDokumenFormSet(instance=pelatihan)
  
    context = {
        'pelatihan': pelatihan,
        'formset': formset,
        'STATUS_DOKUMEN_KOSONG': STATUS_DOKUMEN_KOSONG,
        'STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI': STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI,
        'STATUS_DOKUMEN_PERLU_REVISI': STATUS_DOKUMEN_PERLU_REVISI,
        'STATUS_DOKUMEN_TERVERIFIKASI': STATUS_DOKUMEN_TERVERIFIKASI,
    }
    return render(request, 'admin_detail_pelatihan.html', context)

def detail(request, pelatihan_id):
    if request.user.profile.is_admin:
        return detail_admin(request, pelatihan_id)
    elif request.user.profile.is_penyelenggara:
        return detail_penyelengara(request, pelatihan_id)
    else:
        return HttpResponse("Unauthorized", status=401)

def edit(request, pelatihan_id):
    #TODO: Role-based access control and date validation
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

        if request.user.profile.is_admin:
            document.status = STATUS_DOKUMEN_TERVERIFIKASI
        else:
            document.status = STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI
        document.file_url.save('blank.pdf', ContentFile(buffer.read()))
        
        buffer.close()
        document.save()
        return redirect('detail', pelatihan_id=pelatihan.id)

    return redirect('detail', pelatihan_id=pelatihan.id)

def download_merged_docs(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)
    
    documents_to_merge = PelatihanDokumen.objects.filter(
        pelatihan=pelatihan
    )

    pdf_merger = PdfMerger()
    for document in documents_to_merge:
        reader = PdfReader(document.file_url.path)
        page = reader.pages[0]
        if page.extract_text().strip(): # Check if the page is not empty
            pdf_merger.append(reader)

    output_buffer = BytesIO()
    pdf_merger.write(output_buffer)
    pdf_merger.close()

    output_buffer.seek(0) # Rewind the buffer to the beginning
    response = HttpResponse(output_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Dokumen Pelatihan-{pelatihan.judul}.pdf"'
    output_buffer.close()
    
    return response