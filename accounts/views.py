from django.shortcuts import render, get_object_or_404
from .models import Profile

def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'profile.html', context)