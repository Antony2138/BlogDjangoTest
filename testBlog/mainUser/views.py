import hashlib
import hmac
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
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


def check_telegram_auth(data: dict) -> bool:
    """ Проверяет подпись данных от Telegram """
    auth_data = data.copy()
    auth_data.pop("hash")
    sorted_data = "\n".join(f"{k}={v}" for k, v in sorted(auth_data.items()))
    telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
    secret_key = hashlib.sha256(telegram_bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, sorted_data.encode(), hashlib.sha256).hexdigest()
    print("calculated_hash", calculated_hash)
    print("hash", data["hash"])
    return calculated_hash == data["hash"]


def telegram_auth(request):
    """ Обрабатывает вход через Telegram """
    data = request.GET.dict()
    print("data", data)
    # Проверка срока действия (например, 10 минут)
    if int(data.get("auth_date", 0)) < time.time() - 600:
        return JsonResponse({"error": "Auth expired"}, status=400)

    if not check_telegram_auth(data):
        return JsonResponse({"error": "Invalid auth"}, status=400)

    telegram_id = data["id"]
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    data.get("username", "")

    username = f"tg_{telegram_id}"
    user, created = get_user_model().objects.get_or_create(
        username=username,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        })

    login(request, user)

    return redirect("home")
