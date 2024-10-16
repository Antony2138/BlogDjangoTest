
from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('about', views.about, name='about'),
    path('style', views.style, name='style'),
    path('promo', views.promo, name='promo'),
    path('appointment/', include('appointment.urls')),
    path('calendar', views.calendar, name='calendar'),
    path('', include('mainUser.urls'), name='login'),
    path('', include('appointment.urls'), name='app-admin')

]