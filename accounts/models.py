import random, string
from django.db import models
from django.contrib.auth.models import User

# NOTE: Setup MEDIA_ROOT
def upload_to_foto(instance, filename):
    id_pelatihan = instance.pelatihan.id
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    file_ext = filename.split('.')[-1]
    return f'dokumen/{id_pelatihan}/{instance.nama}{random_string}.{file_ext}'

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
    foto = models.ImageField(upload_to='media/foto_user/', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.role}"