from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.my_profile_view, name='my_profile'),
    path('<int:user_id>/', views.user_profile_view, name='user_profile'),
    path('manage/', views.manage, name='manage'),
    path('add/', views.add_user_view, name='add_user'),
    path('<int:user_id>/delete/', views.delete_user_view, name='delete_user'),
]