from django.contrib.auth import get_user_model
from django.shortcuts import render

# Create your views here.


def index(request):
    admin_user = get_user_model().objects.get(is_superuser=True)
    return render(request, "mainController/index.html", context={"admin": admin_user})


def about(request):
    return render(request, "mainController/about.html")


def style(request):
    return render(request, "mainController/style.html")


def promo(request):
    return render(request, "mainController/promo.html")


def calendar_style(request):
    return render(request, "mainController/calendar.html")
