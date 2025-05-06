# Create your models here.
import random

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    social_link_vk = models.CharField(max_length=160, null=True, blank=True)
    social_link_tg = models.CharField(max_length=160, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    avatar = models.ImageField(upload_to="avatar/", blank=True, null=True)
    confirmed_credentials = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_avatar_url(self):
        if not self.avatar:
            return ""
        return self.avatar.url

    def is_tg_user(self):
        if not self.telegram_id:
            return False
        return True


class EmailVerificationCode(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    # meta data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}"

    @classmethod
    def generate_code(cls, user):
        code = f"{random.randint(100000, 999999)}"
        verification_code = cls(user=user, code=code)
        verification_code.save()
        return code

    def check_code(self, code):
        return self.code == code
