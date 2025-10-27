from django.shortcuts import render, redirect
from pelatihan.models import Pelatihan
from konfigurasi.models import TahunAnggaran
from django.contrib.auth.decorators import login_required

# Create your views here.
def landing_page(request):
    user = request.user
    if user.is_authenticated:
        return redirect('main:dashboard')
    return render(request, 'landing_page.html')

@login_required
def dashboard(request):
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
    return render(request, 'dashboard.html', context)