import json
from django.shortcuts import render
from django.db.models import Count, Sum, Q
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from pelatihan.models import Pelatihan
from konfigurasi.models import TahunAnggaran, Kejuruan, Role
from django.contrib.auth import get_user_model

User = get_user_model()

@admin_required # Dasbor ini mungkin hanya untuk Admin
def dashboard_evaluasi(request):
    context = {}
    tahun_aktif = TahunAnggaran.get_aktif()

    # --- 1. Grafik: Target vs Realisasi Paket (5 Tahun Terakhir) ---
    tahuns = TahunAnggaran.objects.annotate(
        realisasi=Count('pelatihan') # 'pelatihan' = related_name dari Pelatihan.tahun_anggaran
    ).order_by('-tahun')[:5]
    
    # Balik urutannya agar kronologis (tahun terlama ke terbaru)
    tahuns_list = reversed(list(tahuns)) 
    
    labels_target_vs_realisasi = []
    data_target = []
    data_realisasi = []
    
    for ta in tahuns_list:
        labels_target_vs_realisasi.append(ta.tahun)
        data_target.append(ta.target)
        data_realisasi.append(ta.realisasi)

    context['chart_target_realisasi_labels'] = json.dumps(labels_target_vs_realisasi)
    context['chart_target_realisasi_data_target'] = json.dumps(data_target)
    context['chart_target_realisasi_data_realisasi'] = json.dumps(data_realisasi)

    # --- 2. Grafik: Distribusi Paket per PIC (Tahun Ini) ---
    labels_pic = []
    data_pic = []
    if tahun_aktif:
        # Ambil Penyelenggara yang memiliki setidaknya 1 paket di tahun aktif
        pics = User.objects.filter(role__id=Role.PENYELENGGARA).annotate(
            jumlah_paket=Count('pelatihan', filter=Q(pelatihan__tahun_anggaran=tahun_aktif))
        ).filter(jumlah_paket__gt=0).order_by('-jumlah_paket')
        
        for pic in pics:
            labels_pic.append(pic.get_full_name() or pic.username)
            data_pic.append(pic.jumlah_paket)
            
    context['chart_pic_labels'] = json.dumps(labels_pic)
    context['chart_pic_data'] = json.dumps(data_pic)

    # --- 3. Grafik: Total JP per Tahun Anggaran (5 Tahun Terakhir) ---
    tahuns_jp = TahunAnggaran.objects.annotate(
        total_jp=Sum('pelatihan__durasi_jp') # Asumsi field durasi Anda adalah durasi_jp
    ).filter(total_jp__gt=0).order_by('-tahun')[:5]
    
    labels_jp = []
    data_jp = []
    
    for ta in reversed(list(tahuns_jp)):
        labels_jp.append(ta.tahun)
        data_jp.append(ta.total_jp)

    context['chart_jp_labels'] = json.dumps(labels_jp)
    context['chart_jp_data'] = json.dumps(data_jp)

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

    context['chart_kejuruan_labels'] = json.dumps(labels_kejuruan)
    context['chart_kejuruan_data'] = json.dumps(data_kejuruan)
    
    # Kirim tahun_aktif untuk referensi di template
    context['tahun_aktif'] = tahun_aktif
    
    return render(request, 'evaluasi/dashboard_evaluasi.html', context)