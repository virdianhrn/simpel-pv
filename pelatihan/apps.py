from django.apps import AppConfig


class PelatihanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pelatihan'

    def ready(self):
        from . import signals