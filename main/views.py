from django.shortcuts import render
from accounts.models import Profile
# Create your views here.
def landing_page(request):
    user = request.user
    if user.is_authenticated:
        if user.profile.role == Profile.ADMIN:
            return render(request, 'landing_page.html')
        elif user.profile.role == Profile.PENYELENGGARA:
            return render(request, 'landing_page.html')
    return render(request, 'landing_page.html')