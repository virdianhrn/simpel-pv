from django.db import models
from django.contrib.auth.models import User

# NOTE: Setup MEDIA_ROOT
class Profile(models.Model):
    ADMIN = "AD"
    PENYELENGGARA = "PL"

    USER_ROLES = [
        (ADMIN, 'Admin'),
        (PENYELENGGARA, 'Penyelenggara')
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=2, choices=USER_ROLES)
    jabatan = models.CharField(max_length=255, blank=True)
    foto = models.ImageField(upload_to='foto_user/', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.role}"