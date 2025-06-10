from django.shortcuts import render
from pelatihan.models import Pelatihan

def dashboard(request):
    semua_pelatihan = Pelatihan.objects.all()
    
    context = {
        'daftar_pelatihan': semua_pelatihan,
    }
    
    # Merender template HTML dengan konteks yang diberikan
    return render(request, 'dashboard.html', context)