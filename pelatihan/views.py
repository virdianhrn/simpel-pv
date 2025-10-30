# Standard library imports
import json
from io import BytesIO
from datetime import datetime
import os
import tempfile
import subprocess

# Third-party imports
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docxtpl import DocxTemplate

# Local application imports
from accounts.decorators import admin_required, admin_or_pelatihan_owner_required
from .forms import LampiranFormSet, PelatihanForm, VerifikasiLampiranForm, InstrukturFormSet
from .models import Pelatihan, PelatihanLampiran
from konfigurasi.models import StatusDokumen

@admin_required
def verifikasi_dokumen(request, pelatihan_id, document_id):
    document = get_object_or_404(PelatihanLampiran, pk=document_id)

    if request.method == 'POST':
        form = VerifikasiLampiranForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'status': str(document.status)})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    form = VerifikasiLampiranForm(instance=document)
    return render(request, 'form_verifikasi.html', {'form': form, 'document': document})

class DetailView(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):    
        self.pelatihan = get_object_or_404(Pelatihan, id=kwargs.get('pelatihan_id'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests (when a user just views the page).
        """
        formset = LampiranFormSet(instance=self.pelatihan)

        context = {
            'pelatihan': self.pelatihan,
            'formset': formset
        }
        # Render the single, merged template
        return render(request, 'detail_pelatihan.html', context)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests (when a user uploads or verifies a document).
        """
        formset = LampiranFormSet(request.POST, request.FILES, instance=self.pelatihan)

        if formset.is_valid():
            # Handle the data submission
            if request.user.is_admin:
                messages.success(request, 'Verifikasi dokumen berhasil disimpan!')
            else:
                for form in formset:
                    if 'file_url' in form.changed_data:
                        form.instance.status_id = StatusDokumen.DALAM_PROSES_VERIFIKASI
                        break
                messages.success(request, 'Dokumen berhasil diunggah!')
            formset.save()
        else:
            # Handle form errors
            for form in formset:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)
        
        # Always redirect back to the same page after a POST
        return redirect('pelatihan:detail', pelatihan_id=self.pelatihan.id)

@admin_required
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
    return render(request, 'add_pelatihan.html', context)

@admin_or_pelatihan_owner_required
def edit(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)

    referer_url = request.META.get('HTTP_REFERER', reverse('main:dashboard'))

    if request.method == 'POST':
        form = PelatihanForm(request.POST, instance=pelatihan, user=request.user)
        instruktur_formset = InstrukturFormSet(request.POST, instance=pelatihan)
        if form.is_valid() and instruktur_formset.is_valid():
            form.save()
            instruktur_formset.save()
            messages.success(request, f"Pelatihan '{pelatihan.judul}' berhasil diperbarui.")
            return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    else:
        form = PelatihanForm(instance=pelatihan, user=request.user)
        instruktur_formset = InstrukturFormSet(instance=pelatihan)

    context = {
        'form': form,
        'instruktur_formset': instruktur_formset,
        'pelatihan': pelatihan,
        'previous_url': referer_url
    }
    return render(request, 'form_pelatihan.html', context)

@admin_or_pelatihan_owner_required
def skip_document(request, pelatihan_id, document_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)

    if request.method == 'POST':
        document = get_object_or_404(PelatihanLampiran, pk=document_id)
        buffer = BytesIO()
        writer = PdfWriter()

        writer.add_blank_page(width=595, height=842) # A4 size in points
        writer.write(buffer)
        buffer.seek(0)

        if request.user.is_admin:
            document.status_id = StatusDokumen.TERVERIFIKASI
        else:
            document.status_id = StatusDokumen.DALAM_PROSES_VERIFIKASI
        document.file_url.save('blank.pdf', ContentFile(buffer.read()))
        
        buffer.close()
        document.save()
        messages.success(request, f"Dokumen '{document.get_nama_display()}' berhasil di-skip.")
        return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

@admin_or_pelatihan_owner_required
def delete(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    if request.method == 'POST':
        pelatihan_title = pelatihan.judul
        pelatihan.delete()
        messages.success(request, f"Pelatihan '{pelatihan_title}' berhasil dihapus.")
        return redirect('main:dashboard')
    
    return redirect('main:dashboard')

def _generate_report_docx(pelatihan: Pelatihan) -> BytesIO | None:
    """Mengisi template DOCX dengan data pelatihan dan mengembalikan buffer BytesIO."""
    
    instrukturs = pelatihan.instruktur_set.select_related('instruktur').all()
    instruktur_materi_parts = []
    for item in instrukturs:
        nama_instruktur = item.instruktur.nama if item.instruktur else "Nama Tidak Tersedia"
        materi_ajar = item.materi if item.materi else "Materi Tidak Spesifik"
        
        part = f"{nama_instruktur} dengan materi ajar {materi_ajar}"
        instruktur_materi_parts.append(part)

    instruktur_materi_string = "; ".join(instruktur_materi_parts)

    lower_first = lambda s: s[:1].lower() + s[1:] if s else ''
    alasan_belum_lulus = f"Alasan peserta pelatihan tersebut dinyatakan Belum Lulus (BL) adalah dikarenakan {lower_first(pelatihan.alasan_belum_lulus)}"
    blm_lulus_text = f" dan {pelatihan.jumlah_belum_lulus} orang peserta pelatihan yang dinyatakan Belum Lulus (BL). {alasan_belum_lulus}" if (pelatihan.jumlah_belum_lulus > 0) else ''

    context = {
        'judul_lengkap': f"{pelatihan.judul} {pelatihan.paket_ke}",
        'kejuruan': str(pelatihan.kejuruan), 'tempat_pelaksanaan': pelatihan.tempat_pelaksanaan, 'tahun_anggaran': str(pelatihan.tahun_anggaran),
        'jenis_pelatihan': pelatihan.get_jenis_pelatihan_display(), 'metode': pelatihan.get_metode_display(),
        'tanggal_mulai': (pelatihan.tanggal_mulai_aktual or pelatihan.tanggal_mulai_rencana).strftime('%d %B %Y') if (pelatihan.tanggal_mulai_aktual or pelatihan.tanggal_mulai_rencana) else '-',
        'tanggal_selesai': (pelatihan.tanggal_selesai_aktual or pelatihan.tanggal_selesai_rencana).strftime('%d %B %Y') if (pelatihan.tanggal_selesai_aktual or pelatihan.tanggal_selesai_rencana) else '-',
        'durasi_jp': pelatihan.durasi_jp, 'durasi_hari': pelatihan.durasi_hari(), 'jam_per_hari': pelatihan.jam_per_hari,
        'waktu_pelatihan': pelatihan.waktu_pelatihan or '-', 'penyelenggara': str(pelatihan.penyelenggara),
        'no_sk': pelatihan.no_sk or '-', 'tanggal_sk': pelatihan.tanggal_sk.strftime('%d %B %Y') if pelatihan.tanggal_sk else '-', 'tentang_sk': pelatihan.tentang_sk or '-',
        'total_peserta': pelatihan.jumlah_peserta_laki + pelatihan.jumlah_peserta_perempuan, 'jml_laki': pelatihan.jumlah_peserta_laki, 'jml_perempuan': pelatihan.jumlah_peserta_perempuan,
        'jml_lulus': pelatihan.jumlah_lulus, 'jml_belum_lulus': pelatihan.jumlah_belum_lulus, 'blm_lulus': blm_lulus_text,
        'rata_rata_pendidikan': pelatihan.rata_rata_pendidikan or '-', 'rata_rata_usia': pelatihan.rata_rata_usia or '-',
        'rata_rata_gender': pelatihan.rata_rata_gender_display or '-', 'rata_rata_domisili': pelatihan.rata_rata_domisili or '-',
        'tanggal_ttd': pelatihan.tanggal_penandatangan.strftime('%d %B %Y') if pelatihan.tanggal_penandatangan else '[Tanggal Belum Diisi]',
        'jabatan_ttd': pelatihan.jabatan_penandatangan or '[Jabatan Belum Diisi]', 'nama_ttd': pelatihan.nama_penandatangan or '[Nama Pejabat Belum Diisi]',
        'nip_ttd': pelatihan.nip_penandatangan or '[NIP Belum Diisi]', 'jumlah_instruktur': pelatihan.instruktur_set.count(), 'list_instruktur': instruktur_materi_string,'tanggal_laporan_dibuat': datetime.now().strftime('%d %B %Y'), 
    }

    # Tentukan path template
    template_relative_path = 'docs/laporan-template.docx' 
    template_path = finders.find(template_relative_path)
    if not os.path.exists(template_path):
        print(f"Error: Template laporan DOCX tidak ditemukan di {template_path}")
        return None # Kembalikan None jika template tidak ada

    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        
        docx_buffer = BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        return docx_buffer
    except Exception as e:
        print(f"Error saat generate DOCX: {e}")
        return None

# --- Fungsi 2: Merge Lampiran PDF ---
def _merge_lampiran_pdfs(pelatihan: Pelatihan, request) -> BytesIO:
    """Menggabungkan semua lampiran PDF yang valid (tidak kosong) untuk pelatihan."""
    lampiran_merger = PdfMerger()
    documents_to_merge = PelatihanLampiran.objects.filter(
        pelatihan=pelatihan, 
        file_url__isnull=False
    ).exclude(file_url__exact='').order_by('nama') 

    successful_merges = 0

    for document in documents_to_merge:
        reader = None 
        try:
            if document.file_url:
                pdf_file_object = document.file_url 
                
                try:
                    reader = PdfReader(pdf_file_object)
                except PdfReadError as e: # Tangani error jika file bukan PDF valid saat dibuka
                    print(f"Error (PdfReadError) saat membuka lampiran '{document.get_nama_display()}': {e}")
                    messages.warning(request, f"Gagal membaca lampiran PDF '{document.get_nama_display()}' karena format tidak valid atau rusak. Lampiran ini dilewati.")
                    continue # Lanjut ke dokumen berikutnya jika gagal dibuka

                # --- PENGECEKAN HALAMAN KOSONG ---
                is_blank = False
                if reader.pages:
                    page = reader.pages[0] 
                    has_text = bool(page.extract_text().strip())
                    has_images = bool(page.images) # page.images adalah list, list kosong dievaluasi sbg False
                    if not has_text and not has_images:
                        is_blank = True
                else:
                    is_blank = True 

                # Jika tidak kosong, tambahkan ke merger
                if not is_blank:
                    try:
                        lampiran_merger.append(reader) # Gunakan objek reader
                        successful_merges += 1
                    except Exception as append_error: # Tangani error saat append (misal PDF rusak)
                        messages.warning(request, f"Gagal menggabungkan lampiran '{document.get_nama_display()}': {append_error}. Lampiran ini dilewati.")

        except Exception as e:
            # Tangani error umum lainnya
            print(f"Error umum saat memproses lampiran '{document.get_nama_display()}': {e}")
            messages.warning(request, f"Gagal memproses lampiran '{document.get_nama_display()}': {e}. Lampiran ini dilewati.")

    lampiran_pdf_buffer = BytesIO()
    if successful_merges > 0: 
        try:
            lampiran_merger.write(lampiran_pdf_buffer)
        except Exception as e:
            print(f"Error saat menulis PDF lampiran gabungan: {e}")
            messages.warning(request, f"Gagal menyelesaikan penggabungan lampiran PDF: {e}.")
            lampiran_pdf_buffer = BytesIO() 
             
    lampiran_merger.close() 
    lampiran_pdf_buffer.seek(0)

    return lampiran_pdf_buffer

# --- Fungsi Helper: Konversi DOCX ke PDF ---
def _convert_docx_to_pdf(docx_buffer: BytesIO) -> BytesIO | None:
    """Mengonversi buffer DOCX ke buffer PDF menggunakan libreoffice --headless."""
    temp_docx_path = None
    temp_output_dir = None # Direktori untuk output
    output_pdf_path = None
    report_pdf_buffer = BytesIO()

    try:
        temp_output_dir = tempfile.mkdtemp()

        # Tulis DOCX ke file sementara
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_docx:
            temp_docx.write(docx_buffer.read())
            temp_docx_path = temp_docx.name

        # Tentukan path output PDF yang diharapkan
        output_pdf_filename = os.path.basename(temp_docx_path).replace('.docx', '.pdf')
        output_pdf_path = os.path.join(temp_output_dir, output_pdf_filename)

        process = subprocess.run(
            [
                'libreoffice',
                '--headless', # Mode tanpa GUI
                '--convert-to', 'pdf', # Format output
                '--outdir', temp_output_dir, # Direktori output
                temp_docx_path # File input
            ],
            capture_output=True, text=True, check=True, timeout=60
        )

        # Pastikan file output benar-benar dibuat
        if not os.path.exists(output_pdf_path):
            print(f"Error: File output PDF tidak ditemukan di {output_pdf_path}")
            print("Stderr:", process.stderr)
            return None

        with open(output_pdf_path, 'rb') as f_pdf:
            report_pdf_buffer.write(f_pdf.read())
        report_pdf_buffer.seek(0)
        return report_pdf_buffer

    except FileNotFoundError:
        print("Error: Perintah 'libreoffice' tidak ditemukan. Pastikan LibreOffice terinstal di container.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error saat menjalankan libreoffice (return code {e.returncode}): {e}")
        print("Stderr:", e.stderr)
        return None
    except subprocess.TimeoutExpired:
         print("Error: Proses libreoffice timeout.")
         return None
    except Exception as e:
        print(f"Error lain saat konversi libreoffice: {e}")
        return None
    finally:
        # Hapus file sementara dan direktori
        if temp_docx_path and os.path.exists(temp_docx_path): os.remove(temp_docx_path)
        if output_pdf_path and os.path.exists(output_pdf_path): os.remove(output_pdf_path)
        if temp_output_dir and os.path.exists(temp_output_dir): 
            try:
                os.rmdir(temp_output_dir) # Coba hapus direktori
            except OSError:
                print(f"Peringatan: Tidak dapat menghapus direktori sementara {temp_output_dir}") # Mungkin tidak kosong jika error

# --- Fungsi Helper: Gabungkan Dua PDF ---
def _combine_pdfs(pdf_buffer1: BytesIO, pdf_buffer2: BytesIO) -> BytesIO:
    """Menggabungkan dua buffer PDF menjadi satu buffer PDF."""
    final_merger = PdfWriter()
    final_pdf_buffer = BytesIO()
    
    # Tambahkan halaman dari buffer pertama
    if pdf_buffer1 and pdf_buffer1.getbuffer().nbytes > 0:
         try:
            reader1 = PdfReader(pdf_buffer1)
            for page in reader1.pages:
                final_merger.add_page(page)
         except Exception as e:
            print(f"Error membaca PDF buffer 1: {e}")
            # Mungkin tetap lanjutkan tanpa buffer 1

    # Tambahkan halaman dari buffer kedua
    if pdf_buffer2 and pdf_buffer2.getbuffer().nbytes > 0:
        try:
            reader2 = PdfReader(pdf_buffer2)
            for page in reader2.pages:
                final_merger.add_page(page)
        except Exception as e:
            print(f"Error membaca PDF buffer 2: {e}")
            # Mungkin tetap lanjutkan tanpa buffer 2
            
    final_merger.write(final_pdf_buffer)
    final_pdf_buffer.seek(0)
    return final_pdf_buffer

# --- View Utama (Koordinator) ---
@admin_or_pelatihan_owner_required
def generate_full_report_pdf_view(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)
    
    docx_buffer = _generate_report_docx(pelatihan)
    if not docx_buffer:
        messages.error(request, "Gagal membuat dokumen laporan (template tidak ditemukan atau error render).")
        return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    report_pdf_buffer = _convert_docx_to_pdf(docx_buffer)
    docx_buffer.close() # Tutup buffer docx setelah dibaca
    if not report_pdf_buffer:
        messages.error(request, "Gagal mengonversi laporan ke PDF. Pastikan dependensi (LibreOffice/Word) terinstal dan berfungsi.")
        return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    lampiran_pdf_buffer = _merge_lampiran_pdfs(pelatihan, request)
    final_pdf_buffer = _combine_pdfs(report_pdf_buffer, lampiran_pdf_buffer)
    
    # Tutup buffer sementara
    report_pdf_buffer.close()
    lampiran_pdf_buffer.close()

    if final_pdf_buffer.getbuffer().nbytes == 0:
         messages.error(request, "Gagal membuat PDF akhir (kemungkinan semua bagian gagal diproses).")
         final_pdf_buffer.close()
         return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    response = HttpResponse(final_pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Laporan Lengkap - {pelatihan.judul}.pdf"'
    final_pdf_buffer.close() # Tutup buffer akhir setelah dibaca oleh HttpResponse
    
    return response