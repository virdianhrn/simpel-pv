from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CreateUserForm, EditUserForm
from .decorators import admin_required, self_or_admin_required
# Get the custom User model at the start
User = get_user_model()

@login_required
def my_profile_view(request):
    # This is simpler. The user object is the profile.
    context = {
        'target_user': request.user
    }
    return render(request, 'profile.html', context)

@self_or_admin_required
def user_profile_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    # The 'profile' is now the user object itself.
    context = {
        'target_user': target_user
    }
    return render(request, 'profile.html', context)

@admin_required
def manage(request):
    user_list = User.objects.exclude(pk=request.user.pk).order_by('first_name')
    context = {
        'user_list': user_list,
    }
    return render(request, 'user_manage.html', context)

@admin_required
def add_user_view(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST, request.FILES)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"Pengguna '{new_user.username}' berhasil ditambahkan.")
            return redirect('accounts:manage')
    else:
        form = CreateUserForm()

    context = {
        'form': form
    }
    return render(request, 'user_form.html', context)

@admin_required
def edit_user_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, request.FILES, instance=target_user, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Profil untuk '{target_user.username}' berhasil diperbarui.")
            return redirect('accounts:user_profile', user_id=target_user.id)
    else:
        form = EditUserForm(instance=target_user, user=request.user)
    
    context = {
        'form': form,
        'target_user': target_user
    }
    return render(request, 'user_form.html', context)

@admin_required
def delete_user_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    is_own_account = (request.user == target_user)

    if request.method == 'POST':
        user_fullname = target_user.get_full_name()
        if is_own_account:
            logout(request)
            target_user.delete()
            return redirect('core:landing_page')
        else:
            target_user.delete()
            messages.success(request, f"Pengguna '{user_fullname}' berhasil dihapus.")
            return redirect('accounts:manage')
    
    context = {
        'target_user': target_user
    }
    return render(request, 'delete_account_confirmation.html', context)