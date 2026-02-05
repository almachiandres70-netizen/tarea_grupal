from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

# Registro mínimo: solo usuario y contraseña
class RegistroAdminForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Usuario'}),
            'password1': forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Repetir Contraseña'}),
        }

# Login mínimo
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Contraseña'})
    )
