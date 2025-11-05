# Standard library imports
import json
from io import BytesIO
from datetime import datetime
import os
import tempfile
import subprocess
import shutil

# Third-party imports
import fitz
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.contrib.staticfiles import finders
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from docxtpl import DocxTemplate
from PyPDF2.errors import PdfReadError
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth

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

# --- Fungsi Helper: Untuk mengecek PDF kosong ---
def _is_pdf_blank(file_object) -> bool:
    """Mengecek apakah file PDF (gambar atau teks) kosong atau tidak valid."""
    if not file_object:
        return True
    
    reader = None
    try:
        file_object.seek(0)
        reader = PdfReader(file_object)
        
        if not reader.pages:
            return True # Tidak ada halaman
        
        page = reader.pages[0] 
        has_text = bool(page.extract_text().strip())
        has_images = bool(page.images)
        
        if not has_text and not has_images:
            return True # Anggap kosong
        
        return False # Ada konten
        
    except Exception as e:
        print(f"Error _is_pdf_blank: {e}. File dianggap kosong.")
        return True
    finally:
        if file_object:
            file_object.seek(0)

# --- Fungsi Helper: Untuk membuat halaman pemisah PDF ---
def _create_separator_page_pdf(nomor: int, nama: str) -> BytesIO:
    """Membuat PDF satu halaman (A4) dengan teks di tengah."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4 
    margin_horizontal = 2.5 * cm
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2.0, height / 2.0 + (1*cm), f"LAMPIRAN {nomor}")

    c.setFont("Helvetica-Bold", 18) 
    maxWidth = width - (2 * margin_horizontal)
    fontName = "Helvetica-Bold"
    fontSize = 18
    line_height = 22
    
    lines = simpleSplit(nama, fontName, fontSize, maxWidth)
    
    current_y = height / 2.0 - (1*cm) 
    for line in lines:
        c.drawCentredString(width / 2.0, current_y, line)
        current_y -= line_height 

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- Fungsi Helper: Konversi DOCX ke PDF ---
def _convert_docx_to_pdf_simple(docx_buffer: BytesIO) -> BytesIO | None:
    """Mengonversi DOCX ke PDF menggunakan --convert-to (tanpa update TOC)."""
    temp_docx_path = None
    temp_output_dir = None
    output_pdf_path = None
    report_pdf_buffer = BytesIO()
    LIBREOFFICE_PATH = 'libreoffice'
    try:
        temp_output_dir = tempfile.mkdtemp()
        temp_profile_dir = os.path.join(temp_output_dir, "lo_profile")
        os.makedirs(temp_profile_dir)
        user_profile_arg = f"-env:UserInstallation=file://{temp_profile_dir}"
        sub_env = os.environ.copy()
        sub_env['HOME'] = temp_profile_dir

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False, dir=temp_output_dir) as temp_docx:
            temp_docx.write(docx_buffer.read())
            temp_docx_path = temp_docx.name

        output_pdf_filename = os.path.basename(temp_docx_path).replace('.docx', '.pdf')
        output_pdf_path = os.path.join(temp_output_dir, output_pdf_filename)

        print(f"Langkah Konversi: Mengonversi {temp_docx_path} ke PDF...")
        convert_process = subprocess.run(
            [
                LIBREOFFICE_PATH, user_profile_arg,
                '--headless', '--nologo', '--norestore',
                '--convert-to', 'pdf',
                '--outdir', temp_output_dir, 
                temp_docx_path 
            ],
            capture_output=True, text=True, check=True, timeout=60, env=sub_env
        )
        print("Konversi PDF selesai.")

        if not os.path.exists(output_pdf_path):
            print(f"Error: File output PDF tidak ditemukan di {output_pdf_path}")
            print("Stderr (Konversi):", convert_process.stderr)
            return None

        with open(output_pdf_path, 'rb') as f_pdf:
            report_pdf_buffer.write(f_pdf.read())
        report_pdf_buffer.seek(0)
        return report_pdf_buffer
    except Exception as e:
        print(f"Error saat konversi PDF sederhana: {e}")
        return None
    finally:
        if temp_output_dir and os.path.exists(temp_output_dir): 
            try: shutil.rmtree(temp_output_dir)
            except OSError as e: print(f"Peringatan: Gagal hapus temp dir {temp_output_dir}: {e}")

# --- Fungsi Helper: Generate DOCX (Diperbarui untuk menerima context) ---
def _generate_report_docx(pelatihan: Pelatihan, context: dict, template_name: str) -> BytesIO | None:
    """Mengisi template DOCX yang spesifik dengan data dari context."""
    template_relative_path = f'docs/{template_name}' 
    template_path = finders.find(template_relative_path) 
    if not template_path:
        print(f"Error: Template laporan DOCX '{template_relative_path}' tidak ditemukan.")
        return None
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)
        docx_buffer = BytesIO()
        doc.save(docx_buffer)
        docx_buffer.seek(0)
        return docx_buffer
    except Exception as e:
        print(f"Error saat generate DOCX ({template_name}): {e}")
        return None

def _int_to_roman_lower(num):
    """Konversi integer ke angka Romawi huruf kecil (misal: ii, iii, iv)"""
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''; i = 0
    while num > 0:
        for _ in range(num // val[i]): roman_num += syb[i]; num -= val[i]
        i += 1
    return roman_num.lower()

def _extract_toc_data(pdf_buffer: BytesIO) -> (dict, list):
    """Menganalisis buffer PDF KONTEN UTAMA untuk menemukan nomor halaman."""
    toc_data = {}
    pdf_buffer.seek(0)
    
    # Definisikan struktur TOC Anda persis seperti contoh
    # (Teks yang dicari di PDF, Teks yang akan dicetak di TOC, Level Indentasi)
    TOC_STRUCTURE = [
        ('BAB I PENDAHULUAN', 'BAB I PENDAHULUAN', 1),
        ('A. Latar Belakang', 'A. Latar Belakang', 2),
        ('B. Dasar Pelaksanaan', 'B. Dasar Pelaksanaan', 2),
        ('C. Maksud dan Tujuan', 'C. Maksud dan Tujuan', 2),
        ('D. Sasaran Pelatihan', 'D. Sasaran Pelatihan', 2),
        ('BAB II METODE PELAKSANAAN', 'BAB II METODE PELAKSANAAN', 1),
        ('A. Metode Pelaksanaan', 'A. Metode Pelaksanaan', 2),
        ('B. Kompetensi Penunjang', 'B. Kompetensi Penunjang', 2),
        ('BAB III PELAKSANAAN KEGIATAN', 'BAB III PELAKSANAAN KEGIATAN', 1),
        ('A. Kepesertaan', 'A. Kepesertaan', 2),
        ('B. Tenaga Pengajar / Instruktur', 'B. Tenaga Pengajar / Instruktur', 2),
        ('C. Waktu dan Tempat Pelaksanaan', 'C. Waktu dan Tempat Pelaksanaan', 2),
        ('D. Sumber Biaya', 'D. Sumber Biaya', 2),
        ('E. Materi Pelatihan', 'E. Materi Pelatihan', 2),
        ('F. Pelaksanaan Pelatihan', 'F. Pelaksanaan Pelatihan', 2),
        ('BAB IV EVALUASI DAN SARAN', 'BAB IV EVALUASI DAN SARAN', 1),
        ('A. Evaluasi', 'A. Evaluasi', 2), 
        ('B. Saran', 'B. Saran', 2),
        ('BAB V PENUTUP', 'BAB V PENUTUP', 1)
    ]
    
    found_data = {}
    
    try:
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        
        for page_num in range(len(doc)):
            page_index_arab = page_num + 1
            
            # --- PERUBAHAN DIMULAI DI SINI ---
            
            # 1. Dapatkan teks mentah (mungkin mengandung \n)
            page_text_raw = doc.load_page(page_num).get_text("text")
            
            # 2. Normalisasi teks: ganti newline dengan spasi
            page_text_normalized = page_text_raw.replace('\n', ' ')
            
            # 3. Normalisasi teks: rapatkan spasi ganda menjadi tunggal
            page_text = ' '.join(page_text_normalized.split()) 

            # --- AKHIR PERUBAHAN ---
            
            # Cari kunci di halaman ini (sekarang menggunakan page_text yang sudah bersih)
            for search_key, label, level in TOC_STRUCTURE:
                if search_key not in found_data and search_key in page_text:
                    found_data[search_key] = {
                        'label': label,
                        'level': level,
                        'page_arab': page_index_arab 
                    }
        
        doc.close()
        print(f"Ekstraksi TOC selesai. Data: {found_data}")
        
    except Exception as e:
        print(f"Error saat mengekstrak teks (PyMuPDF): {e}")
    
    pdf_buffer.seek(0)
    return found_data, TOC_STRUCTURE

def _create_toc_pdf(cover_page_count: int, toc_page_count: int, daftar_lampiran_page_count: int, 
                    toc_data: dict, toc_structure: list) -> BytesIO:
    """Membuat PDF halaman Daftar Isi multi-level dengan format yang rapi."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2.5 * cm
    
    y = height - margin - (1*cm) # Posisi Y awal
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, y, "DAFTAR ISI")
    y -= (1.5 * cm)

    line_height = 20 # Jarak antar baris
    fontName = "Helvetica"
    fontNameBold = "Helvetica-Bold"
    fontSize = 12
    x_start = margin
    x_end = width - margin
    
    # --- Fungsi Helper Internal ---
    def drawTOCEntry(c, y, label, page_num_str, level):
        """Menggambar satu baris entri Daftar Isi dengan rapi."""
        
        # 1. Atur Font dan Indentasi berdasarkan level
        if level == 1: # BAB
            c.setFont(fontNameBold, fontSize)
            indent = 0
        elif level == 2: # Sub-bab
            c.setFont(fontName, fontSize)
            indent = 1 * cm
        else: # Front matter (Kata Pengantar, dll)
            c.setFont(fontNameBold, fontSize)
            indent = 0
        
        x_label = x_start + indent
        
        # 2. Gambar Label (Teks Kiri)
        c.drawString(x_label, y, label)
        
        # 3. Gambar Nomor Halaman (Teks Kanan)
        # Gunakan font yang sama dengan label agar rata
        page_num_width = stringWidth(page_num_str, c._fontname, c._fontsize)
        x_page_num = x_end - page_num_width
        c.drawString(x_page_num, y, page_num_str)

        # 4. Gambar Garis Titik-titik (Dot Leader)
        label_width = stringWidth(label, c._fontname, c._fontsize)
        x_label_end = x_label + label_width
        x_page_num_start = x_page_num
        
        gap = 0.2 * cm # Jarak 2mm di kiri dan kanan titik-titik
        x_dots_start = x_label_end + gap
        x_dots_end = x_page_num_start - gap
        
        # Y posisinya sedikit di atas baseline font
        y_dots = y + (fontSize * 0.2) 

        if x_dots_start < x_dots_end:
            c.saveState() # Simpan pengaturan grafis
            c.setDash(1, 2) # Atur pola garis: 1pt gambar, 2pt spasi
            c.setStrokeColorRGB(0.5, 0.5, 0.5) # Warna abu-abu (opsional)
            c.line(x_dots_start, y_dots, x_dots_end, y_dots) # Gambar garis
            c.restoreState() # Kembalikan ke pengaturan awal (garis solid, hitam)

    # --- Akhir Fungsi Helper ---


    # 1. Gambar Front Matter
    y -= (0.5 * cm)
    drawTOCEntry(c, y, "KATA PENGANTAR", _int_to_roman_lower(cover_page_count), 0)
    y -= line_height
    drawTOCEntry(c, y, "DAFTAR ISI", _int_to_roman_lower(cover_page_count + toc_page_count), 0)
    y -= line_height
    drawTOCEntry(c, y, "DAFTAR LAMPIRAN", _int_to_roman_lower(cover_page_count + toc_page_count + daftar_lampiran_page_count), 0)
    y -= line_height
    
    # 2. Gambar Konten Utama (Halaman Arab)
    for search_key, label, level in toc_structure:
        found_data = toc_data.get(search_key)
        
        if found_data and level > 0: # Hanya proses BAB dan Sub-bab
            page_num_arab = str(found_data['page_arab'])
            
            if level == 1:
                y -= (0.5 * cm) # Spasi ekstra sebelum BAB baru
            
            drawTOCEntry(c, y, label, page_num_arab, level)
            y -= line_height
    
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def _create_daftar_lampiran_pdf(lampiran_list: list) -> BytesIO:
    """Membuat PDF satu halaman (A4) untuk Daftar Lampiran."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2.5 * cm
    
    y = height - margin - (1*cm) # Posisi Y awal
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, y, "DAFTAR LAMPIRAN")
    y -= (1.5 * cm)

    c.setFont("Helvetica", 12)
    line_height = 18
    
    # Loop melalui daftar lampiran yang valid
    for item in lampiran_list:
        text = f"Lampiran {item['nomor']}: {item['nama']}"
        c.drawString(margin, y, text)
        y -= line_height
        
        # Jika 'y' terlalu rendah, buat halaman baru (opsional)
        if y < (margin + (2*cm)):
            c.showPage()
            y = height - margin
            c.setFont("Helvetica", 12)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@admin_or_pelatihan_owner_required
def generate_full_report_pdf_view(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, pk=pelatihan_id)
    
    # --- TAHAP 1: PERSIAPAN LAMPIRAN ---
    print("Mulai Tahap 1: Pengecekan Lampiran")
    daftar_lampiran_valid = [] 
    objek_lampiran_valid = [] 
    lampiran_counter = 1
    semua_lampiran = PelatihanLampiran.objects.filter(pelatihan=pelatihan).order_by('nama')
    for document in semua_lampiran:
        if not _is_pdf_blank(document.file_url):
            nama_lampiran = document.get_nama_display()
            daftar_lampiran_valid.append({'nomor': lampiran_counter, 'nama': nama_lampiran})
            objek_lampiran_valid.append(document)
            lampiran_counter += 1
        else:
            print(f"Melewati lampiran kosong: {document.get_nama_display()}")

    # --- TAHAP 2: SIAPKAN CONTEXT ---
    print("Mulai Tahap 2: Persiapan Context")
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
        'durasi_jp': pelatihan.durasi_jp, 'durasi_hari': pelatihan.durasi_hari, 'jam_per_hari': pelatihan.jam_per_hari,
        'waktu_pelatihan': pelatihan.waktu_pelatihan or '-', 'penyelenggara': str(pelatihan.penyelenggara),
        'no_sk': pelatihan.no_sk or '-', 'tanggal_sk': pelatihan.tanggal_sk.strftime('%d %B %Y') if pelatihan.tanggal_sk else '-', 'tentang_sk': pelatihan.tentang_sk or '-',
        'total_peserta': pelatihan.jumlah_peserta_laki + pelatihan.jumlah_peserta_perempuan, 'jml_laki': pelatihan.jumlah_peserta_laki, 'jml_perempuan': pelatihan.jumlah_peserta_perempuan,
        'jml_lulus': pelatihan.jumlah_lulus, 'jml_belum_lulus': pelatihan.jumlah_belum_lulus, 'blm_lulus': blm_lulus_text,
        'rata_rata_pendidikan': pelatihan.rata_rata_pendidikan or '-', 'rata_rata_usia': pelatihan.rata_rata_usia or '-',
        'rata_rata_gender': pelatihan.rata_rata_gender_display or '-', 'rata_rata_domisili': pelatihan.rata_rata_domisili or '-',
        'tanggal_ttd': pelatihan.tanggal_penandatangan.strftime('%d %B %Y') if pelatihan.tanggal_penandatangan else '[Tanggal Belum Diisi]',
        'jabatan_ttd': pelatihan.jabatan_penandatangan or '[Jabatan Belum Diisi]', 'nama_ttd': pelatihan.nama_penandatangan or '[Nama Pejabat Belum Diisi]',
        'nip_ttd': pelatihan.nip_penandatangan or '[NIP Belum Diisi]', 'jumlah_instruktur': pelatihan.instruktur_set.count(), 'list_instruktur': instruktur_materi_string,'tanggal_laporan_dibuat': datetime.now().strftime('%d %B %Y'), 
        'daftar_lampiran': daftar_lampiran_valid,
    }

    # --- TAHAP 3: GENERATE & KONVERSI SEMUA BAGIAN ---
    print("Mulai Tahap 3a: Generate Sampul")
    sampul_docx = _generate_report_docx(pelatihan, context, 'laporan-sampul.docx')
    if not sampul_docx: messages.error(request, "Gagal generate sampul."); return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    sampul_pdf = _convert_docx_to_pdf_simple(sampul_docx); sampul_docx.close()
    if not sampul_pdf: messages.error(request, "Gagal konversi PDF sampul."); return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    
    print("Mulai Tahap 3b: Generate Konten")
    konten_docx = _generate_report_docx(pelatihan, context, 'laporan-template.docx')
    if not konten_docx: messages.error(request, "Gagal generate konten."); return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    konten_pdf = _convert_docx_to_pdf_simple(konten_docx); konten_docx.close()
    if not konten_pdf: messages.error(request, "Gagal konversi PDF konten."); return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)

    print("Mulai Tahap 3c: Membuat PDF Daftar Lampiran")
    daftar_lampiran_pdf = _create_daftar_lampiran_pdf(daftar_lampiran_valid)

    # TAHAP 4: EKSTRAKSI & BUAT TOC
    print("Mulai Tahap 4: Ekstraksi & Buat TOC")
    cover_page_count = 0
    try: 
        sampul_reader_temp = PdfReader(sampul_pdf)
        cover_page_count = len(sampul_reader_temp.pages)
        sampul_pdf.seek(0)
    except: 
        print("Error menghitung halaman sampul, diasumsikan 1")
        cover_page_count = 1
    
    daftar_lampiran_page_count = 1 # Asumsi 1 halaman, bisa dihitung jika perlu
    toc_page_count = 1 # Asumsi 1 halaman
    
    toc_data, toc_structure_list = _extract_toc_data(konten_pdf) 
    
    print("Mulai Tahap 4b: Membuat PDF Daftar Isi...")
    toc_pdf = _create_toc_pdf(cover_page_count, toc_page_count, daftar_lampiran_page_count, toc_data, toc_structure_list)
    
    # --- TAHAP 5: PERSIAPKAN SEMUA BAGIAN PDF DALAM SATU LIST ---
    print("Mulai Tahap 5: Mempersiapkan semua bagian PDF di memori...")
    
    # List untuk menampung semua bagian PDF (sebagai BytesIO)
    pdf_pieces_to_merge = []
    # List untuk stream yang perlu ditutup di akhir
    streams_to_close = [] 
    
    try:
        # 1. Tambahkan Laporan Utama (yang sudah ada di memori)
        pdf_pieces_to_merge.append(sampul_pdf); streams_to_close.append(sampul_pdf)
        pdf_pieces_to_merge.append(toc_pdf); streams_to_close.append(toc_pdf)
        pdf_pieces_to_merge.append(daftar_lampiran_pdf); streams_to_close.append(daftar_lampiran_pdf)
        pdf_pieces_to_merge.append(konten_pdf); streams_to_close.append(konten_pdf)
        
        print(f"Menambahkan {len(pdf_pieces_to_merge)} halaman laporan utama.")

        # 2. Loop & Persiapkan Lampiran (Baca dari disk, salin ke memori)
        for i, document in enumerate(objek_lampiran_valid):
            nomor_lampiran = i + 1
            nama_lampiran = document.get_nama_display()
            
            # 2a. Buat Halaman Pemisah (in-memory)
            print(f"Mempersiapkan Pemisah {nomor_lampiran}: {nama_lampiran}")
            separator_buffer = _create_separator_page_pdf(nomor_lampiran, nama_lampiran)
            pdf_pieces_to_merge.append(separator_buffer)
            streams_to_close.append(separator_buffer) # Tambahkan ke list untuk ditutup

            # 2b. Baca Lampiran dari Disk ke Memori
            print(f"Membaca Lampiran {nomor_lampiran}: {nama_lampiran}")
            file_stream = None
            try:
                file_stream = document.file_url.open('rb')
                # Baca seluruh file ke buffer memori baru
                attachment_buffer = BytesIO(file_stream.read())
                pdf_pieces_to_merge.append(attachment_buffer)
                streams_to_close.append(attachment_buffer) # Tambahkan buffer baru ke list
            except Exception as e:
                print(f"Error saat MEMBACA lampiran '{nama_lampiran}': {e}.")
                messages.warning(request, f"Gagal membaca lampiran '{nama_lampiran}': {e}.")
                if 'attachment_buffer' in locals(): attachment_buffer.close()
                separator_buffer.close() # Tutup juga separatornya jika lampiran gagal
            finally:
                if file_stream:
                    file_stream.close() # TUTUP FILE DISK ASLI SEGERA
        
        # --- TAHAP 6: GABUNGKAN SEMUA BAGIAN DARI MEMORI ---
        print(f"Mulai Tahap 6: Menggabungkan {len(pdf_pieces_to_merge)} bagian PDF...")
        final_merger = PdfMerger() # Gunakan PdfMerger untuk .append()
        
        for i, pdf_buffer in enumerate(pdf_pieces_to_merge):
            try:
                pdf_buffer.seek(0) # Pastikan setiap buffer ada di awal
                final_merger.append(pdf_buffer) # Menggabungkan seluruh PDF (dari memori)
                print(f"Berhasil menggabungkan bagian {i+1}...")
            except Exception as merge_error:
                print(f"Error saat menggabungkan bagian {i+1}: {merge_error}")
                # Coba tambahkan halaman per halaman sebagai fallback
                try:
                    pdf_buffer.seek(0)
                    reader = PdfReader(pdf_buffer)
                    for page in reader.pages:
                        final_merger.add_page(page)
                    print(f"  -> Fallback add_page() berhasil untuk bagian {i+1}.")
                except Exception as page_error:
                    print(f"  -> Fallback add_page() GAGAL untuk bagian {i+1}: {page_error}")
                    messages.warning(request, f"Gagal menggabungkan bagian {i+1} dari laporan.")

        # --- TAHAP 7: TULIS & KIRIM RESPONSE ---
        print("Menyelesaikan PDF akhir.")
        final_pdf_buffer = BytesIO()
        final_merger.write(final_pdf_buffer)
        final_merger.close() # Tutup merger
        final_pdf_buffer.seek(0)
        
        response = HttpResponse(final_pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Laporan Lengkap - {pelatihan.judul}.pdf"'
                
        return response

    except Exception as e:
        # Jika terjadi error besar
        print(f"Terjadi error besar saat membuat laporan: {e}")
        messages.error(request, f"Terjadi error besar saat membuat laporan: {e}")
        return redirect('pelatihan:detail', pelatihan_id=pelatihan.id)
    
    finally:
        # --- TAHAP 8: BERSIHKAN SEMUA STREAM ---
        print(f"Menutup {len(streams_to_close)} stream memori...")
        for stream in streams_to_close:
            try:
                stream.close()
            except Exception as e:
                print(f"Gagal menutup stream: {e}")
        
        # Tutup juga buffer akhir jika sudah dibuat
        if 'final_pdf_buffer' in locals() and final_pdf_buffer and not final_pdf_buffer.closed:
            final_pdf_buffer.close()