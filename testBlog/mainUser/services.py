from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect

from .forms import UserRegisterForm


def handle_user_registration(request):
    form = UserRegisterForm(request.POST)
    if form.is_valid():
        # Создаем пользователя
        user = get_user_model().objects.create_user(
            username=form.cleaned_data['usernamer'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1']
        )
        user.save()
        messages.success(request, "Ваш аккаунт создан. Вы можете войти на сайт.")
        return redirect('login')
    else:
        messages.error(request, "Ошибка регистрации, попробуйте снова.")
