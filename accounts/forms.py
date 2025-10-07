from django import forms
from django.contrib.auth import get_user_model
from konfigurasi.models import Role

# Get the custom User model you defined
User = get_user_model()

class CreateUserForm(forms.ModelForm):
    # Add a password confirmation field, which isn't on the model
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    role = forms.ChoiceField(
        choices=Role.get_choices(),
        widget=forms.RadioSelect,
        required=True,
        label="User Role"
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'role', 'jabatan', 'foto']
        widgets = {
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match.")
        return password2

    def save(self, commit=True):
        # ModelForm's default save() doesn't handle password hashing.
        # We need to override it to use set_password().
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):

    role = forms.ChoiceField(
        choices=Role.get_choices(),
        widget=forms.RadioSelect,
        required=True,
        label="User Role"
    )
    
    class Meta:
        model = User
        # Exclude the password field from the edit form
        fields = ['first_name', 'last_name', 'username', 'email', 'role', 'jabatan', 'foto']
        widgets = {
            'role': forms.RadioSelect,
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'jabatan': forms.TextInput(attrs={'class': 'form-control'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        editing_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # If the user is NOT an admin, hide the role field.
        if editing_user and not editing_user.is_admin:
            if 'role' in self.fields:
                del self.fields['role']