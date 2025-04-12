from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class UserRegisterForm(forms.Form):
    usernamer = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ваш логин"}
        )
    )
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Электронная почта"}
        )
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        )
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Повторите пароль"}
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        pswd = cleaned_data.get("password1")
        pswd2 = cleaned_data.get("password2")

        if pswd2 != pswd:
            self.add_error('password2', 'Введенный пароль не совпадает')
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Неверный логин или пароль.")
        return cleaned_data


class EnterCodeForm(forms.Form):
    code = forms.CharField(label="", max_length=6, required=True)


class ConfirmingCredentialsForm(forms.Form):
    first_name = forms.CharField(label="", max_length=50, required=True)
    last_name = forms.CharField(label="", max_length=50, required=True)


class EnterEmailForm(forms.Form):
    new_email = forms.EmailField(required=True)
