from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.decorators import login_required


# Create your views here.


def registration(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Ваш аккаунт создан: можно войти на сайт.')
            return redirect('login')
        else:
            messages.info(request, f'Такой логин занят')
            return redirect('registration')

    else:
        form = UserRegisterForm()
        return render(request, 'mainUser/registration.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'mainUser/profile.html')
