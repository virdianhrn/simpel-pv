from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.my_profile_view, name='my_profile'),
    path('manage/', views.manage, name='manage'),
    path('add/', views.add_user_view, name='add_user'),

    path('<uuid:user_id>/', views.user_profile_view, name='user_profile'),
    path('<uuid:user_id>/edit/', views.edit_user_view, name='edit_user'),
    path('<uuid:user_id>/delete/', views.delete_user_view, name='delete_user'),
]