from django import forms


class UserRegisterForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ваш логин"}
        )
    )
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Имя"}
        )
    )
    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Фамилия"}
        )
    )
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Электронная почта"}
        )
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        )
    )
    social_link_tg = forms.CharField(
        label="Telegramm",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ссылка на Telegram"}
        )
    )
    social_link_vk = forms.CharField(
        label="VK",
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ссылка на VK"}
        )
    )
    phone_number = forms.CharField(
        label="Номер телефона",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Номер телефона"}
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        social_link_tg = cleaned_data.get("social_link_tg")
        social_link_vk = cleaned_data.get("social_link_vk")

        if not social_link_tg and not social_link_vk:
            self.add_error('social_link_vk', 'Укажите верно хотя бы одно: Telegram или VK.')
            self.add_error('social_link_tg', 'Укажите верно хотя бы одно: Telegram или VK.')
        return cleaned_data
