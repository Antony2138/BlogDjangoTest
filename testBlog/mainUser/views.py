import hashlib
import hmac
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.urls import reverse

from .forms import (ClientProfileForm, ConfirmingCredentialsForm,
                    EnterCodeForm, EnterEmailForm, LoginForm, UserRegisterForm)
from .models import EmailVerificationCode
from .services import check_permissions_to_delete, send_confirmation_code
from .utils.db_helpers import Appointment, get_user_appointment_list

# Create your views here.


def user_login(request):
    registration_form = UserRegisterForm()
    login_form = LoginForm()

    if request.method == "POST":
        if request.POST:
            form = LoginForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if not user.confirmed_credentials:
                        request.session["confirming_credentials_check"] = True
                    else:
                        request.session["confirming_credentials_check"] = False
                    login(request, user)  # Вход пользователя в систему
                    return redirect('home')
                else:
                    messages.warning(request, "Ошибка входа, попробуйте снова.")
    return render(request, 'mainUser/login.html', {'login_form': login_form, "registration_form": registration_form})


@login_required
def profile(request):
    return render(request, "mainUser/profile.html")


@login_required
def reject_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user
    if not check_permissions_to_delete(user, appointment):
        return JsonResponse({"error": "You don't have permissions"}, status=403)
    if request.method == "POST":
        appointment.appointment_request.delete()
        appointment.delete()
        response = HttpResponse(status=204)
        response['HX-Trigger'] = "delete-appt"
        return response
    return render(request, "modal/confirm_user_modal.html", {"appointment": appointment})


@login_required
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
    return calculated_hash == data["hash"]


def telegram_auth(request):
    """ Обрабатывает вход через Telegram """
    data = request.GET.dict()
    # Проверка срока действия (например, 10 минут)
    if int(data.get("auth_date", 0)) < time.time() - 600:
        return JsonResponse({"error": "Auth expired"}, status=400)

    if not check_telegram_auth(data):
        return JsonResponse({"error": "Invalid auth."}, status=400)

    telegram_id = data["id"]
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    username = data.get("username", "")
    photo_url = data.get("photo_url", "")
    user, created = get_user_model().objects.get_or_create(
        username=username,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "telegram_id": telegram_id,
            "photo_url": photo_url
        })
    login(request, user)
    if created:
        request.session["confirming_credentials_check"] = True

    return redirect("home")


@login_required
def show_confirming_credentials_modal(request):
    if not request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    if request.method == "POST":
        form = ConfirmingCredentialsForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.confirmed_credentials = True
            user.save()
            request.session.pop("confirming_credentials_check", None)
            response = HttpResponse()
            response['HX-Redirect'] = reverse('home')
            return response
    form = ConfirmingCredentialsForm()
    return render(request, "modal/confirming_credentials_modal.html", {"form": form})


def handle_user_registration(request):
    form = UserRegisterForm(request.POST)
    if form.is_valid():
        user_email = form.cleaned_data['email']
        username = form.cleaned_data['usernamer']
        existing_email = get_user_model().objects.filter(email=user_email)
        existing_username = get_user_model().objects.filter(username=username)
        if existing_username:
            messages.warning(request, "Такой логин занят")
            return render(request, 'mainUser/login.html', {'form': form, 'show_signup': True})
        if existing_email:
            messages.warning(request, "Ошибка регистрации, попробуйте снова.")
            return redirect("login")

        # Создаем пользователя
        user = get_user_model().objects.create_user(
            username=username,
            email=user_email,
            password=form.cleaned_data['password1'],
            is_active=False,
            confirmed_credentials=False
        )
        user.save()
        request.session["email_to_verify"] = user_email
        send_confirmation_code(user)
        messages.success(request, f"Код подтверждения отправлен вам на: {user_email}")
        return redirect('confirm_email_code')
    else:
        return render(request, 'mainUser/login.html', {'form': form, 'show_signup': True})


def confirm_email_code(request):
    if request.method == "POST":
        user_email = request.session.get("email_to_verify")
        user = get_user_model().objects.get(email=user_email)
        verification_code = EmailVerificationCode.objects.filter(user=user).first()
        print(verification_code, "verification_code")
        form = EnterCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data["code"]
            print(entered_code, "entered_code")
            if verification_code and verification_code.check_code(entered_code):
                user.is_active = True
                user.save()
                verification_code.delete()
                messages.success(request, "Ваш email подтвержден! Можете войти на сайт.")
                request.session.pop("email_to_verify", None)
                return redirect("login")
            else:
                verification_code.delete()
                form = EnterCodeForm()
                messages.warning(request, "Введенный код не совпадает")
                content = loader.render_to_string(
                    'mainUser/enter_verification_code.html',
                    {'form': form, 'messages': messages.get_messages(request), "recheck": True, "EnterEmail": False},
                    request=request
                )
                response = HttpResponse(content)
                return response
    else:
        form = EnterCodeForm()
        return render(request, 'mainUser/enter_verification_code.html', {"form": form})


def resend_code(request):
    user_email = request.session.get("email_to_verify")
    user = get_user_model().objects.get(email=user_email)
    send_confirmation_code(user)
    messages.success(request, f"Новый код подтверждения отправлен вам на: {user_email}")
    form = EnterCodeForm()
    content = loader.render_to_string(
        'mainUser/enter_verification_code.html',
        {'form': form, 'messages': messages.get_messages(request), "recheck": False, "EnterEmail": False},
        request=request
    )
    response = HttpResponse(content)
    return response


def change_email(request):
    user_email = request.session.get("email_to_verify")
    user = get_user_model().objects.get(email=user_email)
    if request.method == "POST":
        form = EnterEmailForm(request.POST)
        if form.is_valid():
            new_user_email = form.cleaned_data["new_email"]
            user.email = new_user_email
            user.save()
            request.session["email_to_verify"] = new_user_email
            return resend_code(request)
    else:
        form = EnterEmailForm()
        messages.success(request, "Введите свою почту")
        content = loader.render_to_string(
            'mainUser/enter_verification_code.html',
            {'form': form, 'messages': messages.get_messages(request), "EnterEmail": True},
            request=request
        )
        response = HttpResponse(content)
        return response


@login_required
def edit_client_profile(request):
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "save_details":
            form = ClientProfileForm(request.POST, request.FILES, instance=user)
            if user.avatar:
                user.avatar.delete()
                user.save()
            if form.is_valid():
                form.save()
                messages.success(request, "Профиль обновлён.")
                return redirect('profile')
        elif action == "delete_avatar":
            if user.avatar:
                user.avatar.delete()
                user.save()
                messages.success(request, "Фото удалено")
            else:
                messages.warning(request, "У вас нет фотографии профиля")
            return redirect('profile')
    else:
        form = ClientProfileForm(instance=user)

    return render(request, "partials/edit_client_profile.html", {"form": form})
