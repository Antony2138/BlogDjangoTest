import datetime

from .forms import ServiceForm
from .models import (
    Appointment, AppointmentRequest,  Config, Service,
    StaffMember
)

from django.utils import timezone
from .utils.db_helpers import (
    get_times_from_config, calculate_slots, exclude_booked_slots, get_weekday_num_from_date,
    get_working_hours_for_staff_and_day, calculate_staff_slots, get_appointments_for_date_and_time
)


def get_available_slots_for_staff(date, staff_member):
    """Calculate the available time slots for a given date and a staff member.

    :param date: The date for which to calculate the available slots
    :param staff_member: The staff member for which to calculate the available slots
    :return: A list of available time slots as strings in the format '%I:%M %p' like ['10:00 AM', '10:30 AM']
    """

    # Check if the staff member works on the provided date
    day_of_week = get_weekday_num_from_date()  # Python's weekday starts from Monday (0) to Sunday (6)
    working_hours_dict = get_working_hours_for_staff_and_day(staff_member, day_of_week)
    if not working_hours_dict:
        return []

    slot_duration = datetime.timedelta(minutes=staff_member.get_slot_duration())
    slots = calculate_staff_slots(date, staff_member)
    appointments = get_appointments_for_date_and_time(date, working_hours_dict['start_time'],
                                                      working_hours_dict['end_time'], staff_member)
    return exclude_booked_slots(appointments, slots, slot_duration)



def get_available_slots(date, appointments):
    """Calculate the available time slots for a given date and a list of appointments.

    :param date: The date for which to calculate the available slot
    :param appointments: A list of Appointment objects
    :return: A list of available time slots as strings in the format '%I:%M %p' like ['10:00 AM', '10:30 AM']
    """

    start_time, end_time, slot_duration, buff_time = get_times_from_config(date)
    now = timezone.now()
    buffer_time = now + buff_time if date == now.date() else now
    slots = calculate_slots(start_time, end_time, buffer_time, slot_duration)
    slots = exclude_booked_slots(appointments, slots, slot_duration)
    return [slot.strftime('%I:%M %p') for slot in slots]


def handle_service_management_request(post_data, files_data=None, service_id=None):
    try:
        if service_id:
            service = Service.objects.get(pk=service_id)
            form = ServiceForm(post_data, files_data, instance=service)
        else:
            form = ServiceForm(post_data, files_data)

        if form.is_valid():
            form.save()
            return form.instance, True, "Service saved successfully."
    except Exception as e:
        return None, False, str(e)


def get_appointments_and_slots(date_, service=None):
    """
    Get appointments and available slots for a given date and service.

    If a service is provided, the function retrieves appointments for that service on the given date.
    Otherwise, it retrieves all appointments for the given date.

    :param date_: datetime.date, the date for which to retrieve appointments and available slots
    :param service: Service, the service for which to retrieve appointments
    :return: tuple, a tuple containing two elements:
        - A queryset of appointments for the given date and service (if provided).
        - A list of available time slots on the given date, excluding booked appointments.
    """
    if service:
        appointments = Appointment.objects.filter(appointment_request__service=service,
                                                  appointment_request__date=date_)
    else:
        appointments = Appointment.objects.filter(appointment_request__date=date_)
    available_slots = get_available_slots(date_, appointments)
    return appointments, available_slots