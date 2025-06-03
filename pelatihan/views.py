from django.http import HttpResponse
from django.shortcuts import render
from pelatihan.models import Pelatihan

def detail(request, pelatihan_id):
    pelatihan = Pelatihan.objects.get(pk=pelatihan_id)
    context = {
        'pelatihan': pelatihan,
        'progress': pelatihan.persentase_progress(),
    }
    return HttpResponse(
        f"You're looking at pelatihan {context['pelatihan'].judul} dengan progress {context['progress']}%."
    )

def edit(request, pelatihan_id):
    pelatihan = Pelatihan.objects.get(pk=pelatihan_id)
    context = {
        'pelatihan': pelatihan
    }
    return HttpResponse(f"You're editing a pelatihan {context['pelatihan'].judul}.")