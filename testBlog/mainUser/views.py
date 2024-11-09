from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import json
from .services import handle_user_registration
from .utils.db_helpers import get_user_appointment_list, convert_appointment_to_json
from datetime import datetime

# Create your views here.


def registration(request):
    return handle_user_registration(request)


@login_required
def profile(request):
    user = request.user
    user_appointments = get_user_appointment_list(user)
    user_appointments_json = convert_appointment_to_json(request, user_appointments)

    appointments_list = []
    for appointment in user_appointments_json:
        appointments_list.append({
            'client_name': appointment.get('client_name', ''),
            'client_email': appointment.get('client_email', ''),
            'client_phone': appointment.get('client_phone', ''),
            'service_name': appointment.get('service_name', ''),
            'start_time': datetime.fromisoformat(appointment.get('start_time')),
            'end_time': datetime.fromisoformat(appointment.get('end_time')),

        })
    print(appointments_list)
    context = {'appointments': appointments_list}
    return render(request, "mainUser/profile.html", context=context)
