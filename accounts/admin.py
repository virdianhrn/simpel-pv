from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Get your custom User model
User = get_user_model()

class CustomUserAdmin(UserAdmin):
    # This inherits from the default UserAdmin, so we get all its features
    
    # This adds your custom fields to the 'Edit User' page in the admin
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {'fields': ('role', 'jabatan', 'foto')}),
    )

    # This adds your custom fields to the 'Add User' page in the admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Fields', {'fields': ('role', 'jabatan', 'foto')}),
    )

    # This adds the 'role' to the list of users in the admin
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')

# Register your custom User model with your custom admin class
admin.site.register(User, CustomUserAdmin)