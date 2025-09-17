from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout

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
    return render(request, 'user_manage.html', context)

def delete_user_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    is_own_account = (request.user == target_user)

    if request.method == 'POST':
        user_fullname = target_user.get_full_name()
        
        if is_own_account:
            logout(request)
            target_user.delete()
            return redirect('main:landing_page')
        
        else:
            target_user.delete()
            messages.success(request, f"Pengguna '{user_fullname}' berhasil dihapus.")
            return redirect('accounts:manage')

    context = {
        'target_user': target_user
    }
    return render(request, 'delete_account_confirmation.html', context)