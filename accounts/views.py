from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.
def login_handler(request):
    error = None
    if(request.user.is_authenticated):
        # return HttpResponseRedirect(reverse('main:homepage'))
        return HttpResponseRedirect('')
    if request.method == "POST" :
        data = request.POST
        user = authenticate(username=data['username'],password=data['password'])
        if user is not None:
            login(request,user)
            return HttpResponseRedirect(request.GET.get('next','/'))
        error = 'Username / password tidak sesuai'
    response = {'error' : error}
    return render(request,'login.html', response)
