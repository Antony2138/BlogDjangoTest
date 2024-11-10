from django.apps import apps
from ..models import CustomUser


Appointment = apps.get_model("appointment", "Appointment")

def get_user_appointment_list(client: CustomUser) -> list:
    """Get a list of appointments for staff member."""
    return Appointment.objects.filter(client=client)
