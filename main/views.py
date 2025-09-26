from django.shortcuts import render, redirect
from pelatihan.models import Pelatihan
from django.contrib.auth.decorators import login_required

# Create your views here.
def landing_page(request):
    user = request.user
    if user.is_authenticated:
        return redirect('main:dashboard')
    return render(request, 'landing_page.html')

@login_required
def dashboard(request):
    if request.user.is_admin:
        pelatihan_list = Pelatihan.objects.all().order_by('-tanggal_mulai')
    else:
        pelatihan_list = Pelatihan.objects.filter(pic=request.user).order_by('-tanggal_mulai')
    context = {
        'pelatihan_list': pelatihan_list
    }
    return render(request, 'dashboard.html', context)