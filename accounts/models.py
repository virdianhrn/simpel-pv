import os, uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

def upload_to_foto(instance, filename):
    extension = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{extension}"
    return f'foto_user/{new_filename}'

class User(AbstractUser):
    # The 'id' field is now a CharField without a default
    id = models.CharField(
        primary_key=True,
        max_length=30, # Increased length to accommodate the prefix
        editable=False
    )

    class Role(models.TextChoices):
        ADMIN = "AD", 'Admin'
        PENYELENGGARA = "PL", 'Penyelenggara'
    
    role = models.CharField(max_length=2, choices=Role.choices)
    jabatan = models.CharField(max_length=255, blank=True)
    foto = models.ImageField(upload_to=upload_to_foto, blank=True)

    def save(self, *args, **kwargs):
        """
        Overrides the default save method to create a custom ID.
        """
        # This check ensures the ID is only generated once, when the user is first created.
        if not self.pk:
            # Example: 'AD_vytxeBfsS5wA48ag54f2yN'
            self.id = f"{self.role}_{shortuuid.uuid()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def is_admin(self):
        return self.role == self.ADMIN

    @property
    def is_penyelenggara(self):
        return self.role == self.PENYELENGGARA