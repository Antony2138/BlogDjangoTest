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


class StaffMember(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    services_offered = models.ManyToManyField(Service)
    slot_duration = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Minimum time for an appointment in minutes, recommended 30."
    )
    lead_time = models.TimeField(
        null=True, blank=True,
        help_text="Time when the staff member starts working."
    )
    finish_time = models.TimeField(
        null=True, blank=True,
        help_text="Time when the staff member stops working."
    )
    appointment_buffer_time = models.FloatField(
        blank=True, null=True,
        help_text='Time between now and the first available slot for the current day (doesn\'t affect tomorrow). '
                  'e.g: If you start working at 9:00 AM and the current time is 8:30 AM and you set it to 30 '
                  'minutes, the first available slot will be at 9:00 AM. If you set the appointment buffer time to '
                  '60 minutes, the first available slot will be at 9:30 AM.'
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





