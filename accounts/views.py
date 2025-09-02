from django.shortcuts import render, get_object_or_404
from .models import Profile
from django.contrib.auth.models import User

def my_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'profile.html', context)


def user_profile_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    profile = target_user.profile

    context = {
        'profile': profile,
        'user': target_user
    }
    return render(request, 'profile.html', context)

def manage(request):
    user_list = User.objects.select_related('profile').exclude(pk=request.user.pk).order_by('first_name')

    context = {
        'user_list': user_list,
    }
    return render(request, 'dashboard.html', context)