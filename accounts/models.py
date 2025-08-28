import random, string
from django.db import models
from django.contrib.auth.models import User

def upload_to_foto(instance, filename):
    extension = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{extension}"
    return f'foto_user/{uuid.uuid4()}{extension}'

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
    foto = models.ImageField(upload_to=upload_to_foto, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"