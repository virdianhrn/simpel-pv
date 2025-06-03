from django.http import HttpResponse
from django.shortcuts import render

def detail(request, pelatihan_id):
    return HttpResponse("You're looking at pelatihan %s." % pelatihan_id)