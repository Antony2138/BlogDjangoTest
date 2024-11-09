from django.apps import apps
from ..models import CustomUser


Appointment = apps.get_model("appointment", "Appointment")

def get_user_appointment_list(client: CustomUser) -> list:
    """Get a list of appointments for staff member."""
    return Appointment.objects.filter(client=client)


def convert_appointment_to_json(request, appointments: list) -> list:
    """Convert a queryset of Appointment objects to a JSON serializable format."""
    su = request.user.is_superuser
    return [{
        "id": appt.id,
        "start_time": appt.get_start_time().isoformat(),
        "end_time": appt.get_end_time().isoformat(),
        "client_name": appt.get_client_name(),
        "url": appt.get_absolute_url(request),
        "service_name": appt.get_service_name() if not su else f"{appt.get_service_name()} ({appt.get_staff_member_name()})",
        "client_email": appt.client.email,
        "client_phone": str(appt.client.phone_number),
        "service_id": appt.get_service().id,
        "staff_id": appt.appointment_request.staff_member.id,
    } for appt in appointments]