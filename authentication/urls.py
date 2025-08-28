from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path("login", views.login_handler, name="login"),
    path("logout", views.logout_handler, name="logout"),
]