from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from functools import wraps
from .models import User
from pelatihan.models import Pelatihan

# This decorator already handles both checks perfectly, so no changes are needed.
# user_passes_test automatically redirects to the login_url if the user is not authenticated.
from django.contrib.auth.decorators import user_passes_test
def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an admin.
    """
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.is_admin,
        redirect_field_name=None
    )
    return decorated_view(view_func)

def penyelenggara_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a Penyelenggara.
    """
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.is_penyelenggara,
        redirect_field_name=None
    )
    return decorated_view(view_func)

def self_or_admin_required(view_func):
    """
    Decorator for views that allows access only to the user themselves or to an admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, user_id, *args, **kwargs):
        # 1. Check if the user is logged in. If not, redirect to the login page.
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        # 2. Grant access if the user is an admin.
        if request.user.is_admin:
            return view_func(request, user_id, *args, **kwargs)
        
        # 3. Grant access if the user is accessing their own record.
        if request.user.id == user_id:
            return view_func(request, user_id, *args, **kwargs)
        
        # 4. If none of the above, deny access.
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You are not allowed to view this page.</p>")
    return _wrapped_view

def admin_or_pelatihan_owner_required(view_func):
    """
    Decorator that checks if the user is an admin or the owner of the Pelatihan object.
    """
    @wraps(view_func)
    def _wrapped_view(request, pelatihan_id, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        pelatihan = get_object_or_404(Pelatihan, id=pelatihan_id)
        
        # Grant access if the user is an admin
        if request.user.is_admin:
            return view_func(request, pelatihan_id, *args, **kwargs)

        # Grant access if the user is the owner (penyelenggara) of the object
        # Assumes the Pelatihan model has a 'penyelenggara' field linked to the User
        if pelatihan.pic == request.user:
            return view_func(request, pelatihan_id, *args, **kwargs)

        # If neither, deny access
        return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You are not authorized to edit this pelatihan.</p>")
    return _wrapped_view