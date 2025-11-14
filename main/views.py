import json
from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q, Prefetch, F, Value, FloatField, Avg
from django.db.models.functions import Coalesce 
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from pelatihan.models import Pelatihan
from konfigurasi.models import TahunAnggaran, Kejuruan, Role, StatusPelatihan
from django.contrib.auth import get_user_model

# Create your views here.
def landing_page(request):
    user = request.user
    if user.is_authenticated:
        if user.is_admin:
            return redirect('main:dashboard')
        else:
            return redirect('main:list')
    
    return render(request, 'landing_page.html')

@admin_required 
def dashboard(request):
    User = get_user_model()
    context = {}
    tahun_aktif = TahunAnggaran.get_aktif()

    # --- 1. Grafik: Target vs Realisasi Paket (5 Tahun Terakhir) ---
    tahuns = TahunAnggaran.objects.annotate(
        realisasi_desimal=Coalesce(
            Sum(
                F('pelatihan__progress_laporan') / 100.0, 
                output_field=FloatField()
            ),
            Value(0.0, output_field=FloatField()) 
        )
    ).order_by('-tahun')[:5]
    
    tahuns_list = reversed(list(tahuns)) 
    labels_target_vs_realisasi = []
    data_target = []
    data_realisasi = []
    for ta in tahuns_list:
        labels_target_vs_realisasi.append(ta.tahun)
        data_target.append(ta.target)
        data_realisasi.append(round(ta.realisasi_desimal, 2)) 

    context['chart_target_realisasi_labels'] = labels_target_vs_realisasi
    context['chart_target_realisasi_data_target'] = data_target
    context['chart_target_realisasi_data_realisasi'] = data_realisasi

    # --- 2. Grafik: Distribusi Paket per PIC (Tahun Ini) ---
    labels_pic = []
    data_pic = []
    if tahun_aktif:
        pics = User.objects.filter(role__id=Role.PENYELENGGARA).annotate(
            jumlah_paket=Count('pelatihan', filter=Q(pelatihan__tahun_anggaran=tahun_aktif))
        ).filter(jumlah_paket__gt=0).order_by('-jumlah_paket')
        for pic in pics:
            labels_pic.append(pic.get_full_name() or pic.username)
            data_pic.append(pic.jumlah_paket)
            
    context['chart_pic_labels'] = labels_pic
    context['chart_pic_data'] = data_pic

    # --- 3. Grafik: Total JP per Tahun Anggaran (5 Tahun Terakhir) ---
    tahuns_jp = TahunAnggaran.objects.annotate(
        total_jp=Coalesce(Sum('pelatihan__durasi_jp'), 0) 
    ).order_by('-tahun')[:5]
    
    labels_jp = []
    data_jp = []
    for ta in reversed(list(tahuns_jp)):
        labels_jp.append(ta.tahun)
        data_jp.append(ta.total_jp)

    context['chart_jp_labels'] = labels_jp
    context['chart_jp_data'] = data_jp

    # --- 4. Grafik: Paket per Kejuruan (Tahun Ini) ---
    labels_kejuruan = []
    data_kejuruan = []
    if tahun_aktif:
        kejuruans = Kejuruan.objects.annotate(
            jumlah_paket=Count('pelatihan', filter=Q(pelatihan__tahun_anggaran=tahun_aktif))
        ).filter(jumlah_paket__gt=0).order_by('-jumlah_paket')
        for k in kejuruans:
            labels_kejuruan.append(k.nama)
            data_kejuruan.append(k.jumlah_paket)

    context['chart_kejuruan_labels'] = labels_kejuruan
    context['chart_kejuruan_data'] = data_kejuruan
    
    # --- 5. [MODIFIED] Grafik: Rata-rata Progress Keseluruhan (Tahun Ini) ---
    context['chart_overall_progress_data'] = None # Default to None
    if tahun_aktif:
        # Aggregate the averages for ALL trainings in the active year
        overall_progress = Pelatihan.objects.filter(
            tahun_anggaran=tahun_aktif
        ).aggregate(
            total_avg_upload=Avg('progress_upload'),
            total_avg_laporan=Avg('progress_laporan')
        )
        
        # Check if data was returned (it might be None if no trainings exist)
        if overall_progress.get('total_avg_upload') is not None:
            context['chart_overall_progress_data'] = {
                'upload': round(overall_progress['total_avg_upload'], 1),
                'laporan': round(overall_progress['total_avg_laporan'], 1)
            }
    
    # --- 6. Grafik: Distribusi Status Pelatihan (Tahun Ini) ---
    labels_status = []
    data_status = []
    if tahun_aktif:
        status_dist = Pelatihan.objects.filter(
            tahun_anggaran=tahun_aktif
        ).values(
            'status__nama'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        for s in status_dist:
            labels_status.append(s['status__nama'])
            data_status.append(s['count'])
    
    context['chart_status_labels'] = labels_status
    context['chart_status_data'] = data_status
    
    context['tahun_aktif'] = tahun_aktif
    
    return render(request, 'dashboard.html', context)

@login_required
def list_pelatihan(request):
    tahun_aktif = TahunAnggaran.get_aktif()
    pelatihan_list = []

    if request.user.is_admin:
        pelatihan_list = Pelatihan.objects.filter(tahun_anggaran=tahun_aktif).order_by('-tanggal_mulai_rencana')
    else:
        pelatihan_list = Pelatihan.objects.filter(
            penyelenggara=request.user, 
            tahun_anggaran=tahun_aktif
        ).order_by('-tanggal_mulai_rencana')
        
    context = {
        'pelatihan_list': pelatihan_list,
        'tahun_aktif': tahun_aktif
    }
    return render(request, 'list_pelatihan.html', context)