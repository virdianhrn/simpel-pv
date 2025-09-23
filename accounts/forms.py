from django import forms
from django.contrib.auth.models import User
from .models import Profile

class CreateUserForm(forms.Form):
    # Fields from the User model
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    # Fields from the Profile model
    role = forms.ChoiceField(choices=Profile.USER_ROLES, widget=forms.RadioSelect, initial=Profile.PENYELENGGARA)
    jabatan = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    foto = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Pengguna dengan username ini sudah ada.")
        return username

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Kedua password tidak sama.")
        return password2

    def save(self):
        # Create the User object
        user = User.objects.create_user(
            username=self.cleaned_data.get('username'),
            password=self.cleaned_data.get('password'),
            email=self.cleaned_data.get('email'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name')
        )

        # Create the Profile object linked to the user
        profile = Profile.objects.create(
            user=user,
            role=self.cleaned_data.get('role'),
            jabatan=self.cleaned_data.get('jabatan'),
            foto=self.cleaned_data.get('foto')
        )
        return user

# in accounts/forms.py

class EditUserForm(forms.Form):
    # Fields from the User model
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    # Fields from the Profile model
    role = forms.ChoiceField(choices=Profile.USER_ROLES, widget=forms.RadioSelect)
    jabatan = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    foto = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        # Get the user performing the edit and the user being edited
        self.editing_user = kwargs.pop('user', None)
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)

        # Pre-populate the form with existing data
        if self.instance:
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['username'].initial = self.instance.username
            self.fields['email'].initial = self.instance.email
            self.fields['role'].initial = self.instance.profile.role
            self.fields['jabatan'].initial = self.instance.profile.jabatan
            self.fields['foto'].initial = self.instance.profile.foto
        
        # If the user is NOT an admin, hide the role field
        if self.editing_user and not self.editing_user.profile.is_admin:
            if 'role' in self.fields:
                del self.fields['role']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username has changed and if the new one is already taken
        if self.instance and self.instance.username != username:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("A user with this username already exists.")
        return username

    def save(self):
        # Update the User object
        user = self.instance
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.username = self.cleaned_data.get('username')
        user.email = self.cleaned_data.get('email')
        user.save()

        # Update the Profile object
        profile = user.profile
        profile.jabatan = self.cleaned_data.get('jabatan')
        
        # Only update the photo if a new one was uploaded
        if self.cleaned_data.get('foto'):
            profile.foto = self.cleaned_data.get('foto')

        # Only admins can change the role
        if self.editing_user.profile.is_admin:
            profile.role = self.cleaned_data.get('role')
        
        profile.save()
        return user