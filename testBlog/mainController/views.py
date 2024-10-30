from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    return render(request, 'mainController/index.html')


def about(request):
    return render(request, 'mainController/about.html')


def style(request):
    return render(request, 'mainController/style.html')


def promo(request):
    return render(request, 'mainController/promo.html')


def calendar_style(request):
    return render(request, 'mainController/calendar.html')
