from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, UserRegisterForm
from .services import handle_user_registration
from .utils.db_helpers import Appointment, get_user_appointment_list

# Create your views here.

def user_login(request):
    registration_form = UserRegisterForm()
    login_form = LoginForm()

    if request.method == "POST":
        if 'login_submit' in request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)  # Вход пользователя в систему
                    return redirect('home')  # Перенаправление после успешного входа
                else:
                    messages.error(request, "Ошибка входа, попробуйте снова.")
        elif 'register_submit' in request.POST:
            handle_user_registration(request)
    return render(request, 'mainUser/login.html', {'login_form': login_form, "registration_form": registration_form})


@login_required
def profile(request):
    return render(request, "mainUser/profile.html")


@login_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == "POST":
        appointment.appointment_request.delete()
        appointment.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = "delete-appt"
        return response
    return render(request, "modal/confirm_user_modal.html", {"appointment": appointment})


def get_clients_appointments(request):
    user = request.user
    user_appointments = get_user_appointment_list(user)
    context = {'appointments': user_appointments}
    return render(request, "partials/get_client_appt.html", context=context)
