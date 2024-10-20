import datetime

from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator, MinValueValidator
from django.conf import settings

# Create your models here.

DAYS_OF_WEEK = (
    (0, 'Sunday'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thursday'),
    (5, 'Friday'),
    (6, 'Saturday'),
)


class Service(models.Model):
    name = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True, null=True)
    duration = models.DurationField(validators=[MinValueValidator(datetime.timedelta(seconds=1))])
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_duration_parts(self):
        total_seconds = int(self.duration.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return days, hours, minutes, seconds

    def get_duration(self):
        days, hours, minutes, seconds = self.get_duration_parts()
        parts = []

        if days:
            parts.append(f"{days} day{'s' if days > 1 else ''}")
        if hours:
            parts.append(f"{hours} час{'а' if hours > 1 else ''}")
        if minutes:
            parts.append(f"{minutes} минут")
        if seconds:
            parts.append(f"{seconds} секунд{'ы' if seconds > 1 else ''}")

        return ' '.join(parts)

    def get_price(self):
        # Check if the decimal part is 0
        return (f"{self.price} рублей")

    def get_description(self):
        return self.description


class StaffMember(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services_offered = models.ManyToManyField(Service)
    slot_duration = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='(Количество слотов доступных для записи к данному работнику, день будет разбит на промежутки по'
                  ' установленному количеству минут)'

    )
    lead_time = models.TimeField(
        null=True, blank=True,
        help_text="Время начала рабочего дня"
    )
    finish_time = models.TimeField(
        null=True, blank=True,
        help_text="Время конца рабочего дня"
    )
    appointment_buffer_time = models.FloatField(
        blank=True, null=True,
        help_text='Время между текущим моментом и первым доступным интервалом на текущий день (не влияет на завтра). '
                  'Например: если вы начинаете работать в 9:00 утра, а текущее время — 8:30 утра, и вы устанавливаете его на 30 '
                  'минут, первый доступный интервал будет в 9:00 утра. Если вы устанавливаете время буфера встреч на '
                  '60 минут, первый доступный интервал будет в 9:30 утра.'
    )


class AppointmentRequest(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    staff_member = models.ForeignKey(StaffMember, on_delete=models.SET_NULL, null=True)
    id_request = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.start_time} to {self.end_time} - {self.service.name}"


class Appointment(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    appointment_request = models.OneToOneField(AppointmentRequest, on_delete=models.CASCADE)
    phone = models.DecimalField(max_digits=8, decimal_places=2)
    id_request = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client} - " \
               f"{self.appointment_request.start_time.strftime('%Y-%m-%d %H:%M')} to " \
               f"{self.appointment_request.end_time.strftime('%Y-%m-%d %H:%M')}"


class Config(models.Model):
    slot_duration = models.PositiveIntegerField(
        null=True,
        help_text="Minimum time for an appointment in minutes, recommended 30."
    )

    lead_time = models.TimeField(
        null=True,
        help_text="Time when we start working."
    )
    finish_time = models.TimeField(
        null=True,
        help_text="Time when we stop working."
    )
    appointment_buffer_time = models.FloatField(
        null=True,
        help_text="Time between now and the first available slot for the current day (doesn't affect tomorrow)."
    )


class WorkingHours(models.Model):
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    day_of_week = models.PositiveIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.start_time} to {self.end_time}"
