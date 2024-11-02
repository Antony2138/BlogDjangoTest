from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserRegisterForm

# Create your views here.


def registration(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Ваш аккаунт создан: можно войти на сайт.")
            return redirect("login")
        else:
            messages.info(request, "Форма заполнена неправильно")
            return redirect("registration")

    else:
        form = UserRegisterForm()
        return render(request, "mainUser/registration.html", {"form": form})


@login_required
def profile(request):
    return render(request, "mainUser/profile.html")
