from django.shortcuts import render, redirect
from accounts.models import Profile
from pelatihan.models import Pelatihan

# Create your views here.
def landing_page(request):
    user = request.user
    if user.is_authenticated:
        return redirect('main:dashboard')
    return render(request, 'landing_page.html')

def dashboard(request):
    pelatihan_list = Pelatihan.objects.all()
    context = {
        'pelatihan_list': pelatihan_list
    }
    return render(request, 'dashboard.html', context)