from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('style', views.style, name='style'),
    path('promo', views.promo, name='promo'),
    path('calendar', views.calendar_style, name='calendar'),

]
