from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='mainUser/login.html'), name='login'),
    path('registration/', views.registration, name="registration"),

]