import os, shortuuid, uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from konfigurasi.models import Role

def upload_to_foto(instance, filename):
    extension = os.path.splitext(filename)[1]
    new_filename = f"{shortuuid.uuid()}{extension}"
    return f'foto_user/{new_filename}'

class User(AbstractUser):
    # The 'id' field is now a CharField without a default
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='users',
        default=Role.PENYELENGGARA
    )
    
    jabatan = models.CharField(max_length=255, blank=True)
    foto = models.ImageField(upload_to=upload_to_foto, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self):
        return self.role.id == Role.ADMIN

    @property
    def is_penyelenggara(self):
        return self.role.id == Role.PENYELENGGARA