from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pelatihan, PelatihanDokumen
from .forms import DokumenFormSet, PelatihanForm, VerifikasiDokumenForm
from django.core.files.base import ContentFile
from io import BytesIO
from PyPDF2 import PdfWriter, PdfMerger, PdfReader
from django.contrib import messages
import json
from django.views import View
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin

DocStatus = PelatihanDokumen.DocumentStatus

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

class DetailView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        """
        This method still runs first. We use it to check permissions
        and get the pelatihan object so we don't have to fetch it twice.
        """
        if not (request.user.is_admin or request.user.is_penyelenggara):
            return HttpResponseForbidden("You are not authorized to view this page.")
        
        self.pelatihan = get_object_or_404(Pelatihan, id=kwargs.get('pelatihan_id'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests (when a user just views the page).
        """
        formset = DokumenFormSet(instance=self.pelatihan)

        context = {
            'pelatihan': self.pelatihan,
            'formset': formset,
            'STATUS_DOKUMEN_KOSONG': DocStatus.KOSONG,
            'STATUS_DOKUMEN_DALAM_PROSES_VERIFIKASI': DocStatus.DALAM_PROSES_VERIFIKASI,
            'STATUS_DOKUMEN_PERLU_REVISI': DocStatus.PERLU_REVISI,
            'STATUS_DOKUMEN_TERVERIFIKASI': DocStatus.TERVERIFIKASI,
        }
        # Render the single, merged template
        return render(request, 'detail_pelatihan.html', context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests (when a user uploads or verifies a document).
        """
        formset = DokumenFormSet(request.POST, request.FILES, instance=self.pelatihan)

        if formset.is_valid():
            # Handle the data submission
            formset.save()
            if request.user.is_admin:
                messages.success(request, 'Verifikasi dokumen berhasil disimpan!')
            else:
                for form in formset:
                    if 'file_url' in form.changed_data:
                        form.instance.status = DocStatus.DALAM_PROSES_VERIFIKASI
                        break
                formset.save()
                messages.success(request, 'Dokumen berhasil diunggah!')
        else:
            # Handle form errors
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        
        # Always redirect back to the same page after a POST
        return redirect('pelatihan:detail', pelatihan_id=self.pelatihan.id)

def add(request):
    if request.method == 'POST':
        form = PelatihanForm(request.POST, user=request.user)
        if form.is_valid():
            pelatihan = form.save()
            messages.success(request, f"Pelatihan '{pelatihan.judul}' berhasil ditambahkan.")
            return redirect('main:dashboard')
    else:
        form = PelatihanForm(user=request.user)

    context = {
        'form': form
    }
    return render(request, 'form_pelatihan.html', context)

def edit(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)

    if request.method == 'POST':
        form = PelatihanForm(request.POST, instance=pelatihan, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Pelatihan '{pelatihan.judul}' berhasil diperbarui.")
            return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    else:
        form = PelatihanForm(instance=pelatihan, user=request.user)

    context = {
        'form': form,
        'pelatihan': pelatihan
    }
    return render(request, 'form_pelatihan.html', context)

def skip_document(request, pelatihan_id, document_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)

    if request.method == 'POST':
        document = get_object_or_404(PelatihanDokumen, pk=document_id)
        buffer = BytesIO()
        writer = PdfWriter()

        writer.add_blank_page(width=595, height=842) # A4 size in points
        writer.write(buffer)
        buffer.seek(0)

        if request.user.is_admin:
            document.status = DocStatus.TERVERIFIKASI
        else:
            document.status = DocStatus.DALAM_PROSES_VERIFIKASI
        document.file_url.save('blank.pdf', ContentFile(buffer.read()))
        
        buffer.close()
        document.save()
        messages.success(request, f"Dokumen '{document.get_nama_display()}' berhasil di-skip.")
        return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)


def delete(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    if request.method == 'POST':
        pelatihan_title = pelatihan.judul
        pelatihan.delete()
        messages.success(request, f"Pelatihan '{pelatihan_title}' berhasil dihapus.")
        return redirect('main:dashboard')
    
    return redirect('main:dashboard')

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