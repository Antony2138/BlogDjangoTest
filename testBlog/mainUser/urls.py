from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path(
        "login/",
        views.user_login,
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="mainUser/logout.html"),
        name="logout",
    ),
    path("profile/", views.profile, name="profile"),
    path("telegram/", views.telegram_auth, name="telegram"),

    path("reject_appointment/<int:appointment_id>", views.reject_appointment, name="reject_appointment"),

    # htmx_get
    path('get_clients_appointments/', views.get_clients_appointments, name='get_clients_appointments'),

]
