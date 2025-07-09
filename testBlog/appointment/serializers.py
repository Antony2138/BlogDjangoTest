from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

Review = apps.get_model("mainController", "Review")


class ClientAnalyticsSerializer(serializers.ModelSerializer):
    registration_date = serializers.SerializerMethodField()
    last_visit = serializers.SerializerMethodField()
    initials = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    total_visits = serializers.IntegerField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'first_name', 'last_name', 'email',
                  'registration_date', 'last_visit',
                  'total_visits', 'total_comments', 'initials', 'avatar']

    def get_registration_date(self, obj):
        return obj.date_joined.strftime('%d.%m.%Y') if obj.date_joined else None

    def get_last_visit(self, obj):
        if hasattr(obj, 'last_visit') and obj.last_visit:
            return self.format_last_visit(obj.last_visit)
        return "––"

    def get_initials(self, obj):
        return f"{obj.first_name[0]}{obj.last_name[0]}".upper() if obj.first_name and obj.last_name else "NN"

    def get_avatar(self, obj):
        if obj.is_tg_user():
            url = obj.get_photo_url()
        else:
            url = obj.get_avatar_url()
        return url

    def format_last_visit(self, date):
        today = timezone.now().date()
        delta = today - date
        if delta.days == 0:
            return "Сегодня"
        elif delta.days == 1:
            return "Вчера"
        elif delta.days < 7:
            match delta.days:
                case 2 | 3 | 4:
                    return f"{delta.days} дня назад"
                case _:
                    return f"{delta.days} дней назад"
        else:
            return date.strftime('%d.%m.%Y')
