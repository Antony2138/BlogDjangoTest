from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import EmailVerificationCode


def generate_unique_username_from_email(email: str) -> str:
    username_base = email.split('@')[0]
    username = username_base
    suffix = 1
    CLIENT_MODEL = get_user_model()

    while CLIENT_MODEL.objects.filter(username=username).exists():
        suffix_str = f"{suffix:02}"
        username = f"{username_base}{suffix_str}"
        suffix += 1
    return username


def send_confirmation_code(user):
    EmailVerificationCode.objects.filter(user=user).delete()
    verification_code = EmailVerificationCode.generate_code(user=user)

    subject = "Подтверждение регистрации:"
    message = f"Здравствуйте, {user.username}! Ваш код подтверждения: {verification_code}"
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(
        subject,
        message,
        from_email,
        [user.email],
        fail_silently=False,
    )
