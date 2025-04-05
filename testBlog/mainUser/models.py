# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    year_of_birth = models.IntegerField(null=True, blank=True)
    social_link_tg = models.CharField(max_length=160, null=True, blank=True)
    social_link_vk = models.CharField(max_length=160, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
