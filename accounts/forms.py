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