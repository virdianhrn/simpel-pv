from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login_handler, name="login"),
    path("login", views.logout_handler, name="logout"),
]