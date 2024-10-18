from django import forms
from django.contrib.auth.models import User


class UserRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        help_texts = {
            'username': None,
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваш логин',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Имя"
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Электронная почта'
            }),
            'password': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите пароль'
            }),
        }
