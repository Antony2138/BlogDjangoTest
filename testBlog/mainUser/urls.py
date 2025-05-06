from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.user_login, name="login"),

    path("registration/", views.handle_user_registration, name="handle_user_registration"),
    path("confirm_email_code/", views.confirm_email_code, name="confirm_email_code"),
    path("resend_code/", views.resend_code, name="resend_code"),
    path("change_email/", views.change_email, name="change_email"),


    path("logout/", auth_views.LogoutView.as_view(template_name="mainUser/logout.html"), name="logout"),

    path("profile/", views.profile, name="profile"),
    path("telegram/", views.telegram_auth, name="telegram"),

    path("show_confirming_credentials_modal/",
         views.show_confirming_credentials_modal,
         name="show_confirming_credentials_modal"),

    path("reject_appointment/<int:appointment_id>", views.reject_appointment, name="reject_appointment"),
    path("edit_user_profile/", views.edit_user_profile, name="edit_user_profile"),

    # htmx_get
    path('get_clients_appointments/', views.get_clients_appointments, name='get_clients_appointments'),

]
