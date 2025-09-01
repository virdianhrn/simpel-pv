from django.shortcuts import render, get_object_or_404
from .models import Profile
from django.contrib.auth.models import User

def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'profile.html', context)

def manage(request):
    user_list = User.objects.select_related('profile').exclude(pk=request.user.pk).order_by('first_name')

    context = {
        'user_list': user_list,
    }
    return render(request, 'dashboard.html', context)