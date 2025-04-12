from django.contrib import admin

from .models import CustomUser, EmailVerificationCode


@admin.register(CustomUser)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")


@admin.register(EmailVerificationCode)
class CodeAdmin(admin.ModelAdmin):
    pass
