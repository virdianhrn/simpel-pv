from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Pelatihan, PelatihanDokumen
from .forms import PelatihanDokumenFormSet

def detail(request, pelatihan_id):
    pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
    
    if request.method == 'POST':
        formset = PelatihanDokumenFormSet(request.POST, request.FILES, instance=pelatihan)
        if formset.is_valid():
            formset.save()
            return redirect('detail', pelatihan_id=pelatihan.id)
    else:
        formset = PelatihanDokumenFormSet(instance=pelatihan)
  
    context = {
        'pelatihan': pelatihan,
        'progress': pelatihan.persentase_progress(),
        'formset': formset
    }
    return render(request, 'detail_pelatihan.html', context)

def edit(request, pelatihan_id):
    pelatihan = Pelatihan.objects.get(pk=pelatihan_id)
    context = {
        'pelatihan': pelatihan
    }
    return HttpResponse(f"You're editing a pelatihan {context['pelatihan'].judul}.")