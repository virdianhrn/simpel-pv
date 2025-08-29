from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def login_handler(request):
    error = None
    if(request.user.is_authenticated):
        return redirect('main:landing_page'))
    if request.method == "POST" :
        data = request.POST
        user = authenticate(username=data['username'],password=data['password'])
        if user is not None:
            login(request,user)
            return redirect(request.GET.get('next','/'))
        error = 'Username / password tidak sesuai'
    response = {'error' : error}
    return render(request,'login.html', response)

def logout_handler(request):
    logout(request)
    return render(request,'logout.html')
