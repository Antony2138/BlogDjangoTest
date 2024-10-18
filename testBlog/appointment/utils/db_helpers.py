from typing import Optional

from django.core.cache import cache
import datetime
from django.apps import apps

from ..settings import(
    APPOINTMENT_BUFFER_TIME, APPOINTMENT_FINISH_TIME, APPOINTMENT_LEAD_TIME,
    APPOINTMENT_SLOT_DURATION
)

from .date_time import combine_date_and_time, get_weekday_num

Appointment = apps.get_model('appointment', 'Appointment')
Config = apps.get_model('appointment', 'Config')
WorkingHours = apps.get_model('appointment', 'WorkingHours')
StaffMember = apps.get_model('appointment', 'StaffMember')


def calculate_slots(start_time, end_time, buffer_time, slot_duration):
    """Calculate the available slots between the given start and end times using the given buffer time and slot duration

    :param start_time: The start time.
    :param end_time: The end time.
    :param buffer_time: The buffer time.
    :param slot_duration: The duration of each slot.
    :return: A list of available slots.
    """
    slots = []
    buffer_time = buffer_time.replace(tzinfo=None)
    while start_time + slot_duration <= end_time:
        if start_time >= buffer_time:
            slots.append(start_time)
        start_time += slot_duration
    return slots


def get_times_from_config(date):
    """Get the start time, end time, slot duration, and buffer time from the configuration or the settings file.

    :param date: The date to get the times for.
    :return: The start time, end time, slot duration, and buffer time.
    """
    config = get_config()
    if config:
        start_time = datetime.datetime.combine(date, datetime.time(hour=config.lead_time.hour,
                                                                   minute=config.lead_time.minute))
        end_time = datetime.datetime.combine(date, datetime.time(hour=config.finish_time.hour,
                                                                 minute=config.finish_time.minute))
        slot_duration = datetime.timedelta(minutes=config.slot_duration)
        buff_time = datetime.timedelta(minutes=config.appointment_buffer_time)
    else:
        start_hour, start_minute = APPOINTMENT_LEAD_TIME
        start_time = datetime.datetime.combine(date, datetime.time(hour=start_hour, minute=start_minute))
        finish_hour, finish_minute = APPOINTMENT_FINISH_TIME
        end_time = datetime.datetime.combine(date, datetime.time(hour=finish_hour, minute=finish_minute))
        slot_duration = datetime.timedelta(minutes=APPOINTMENT_SLOT_DURATION)
        buff_time = datetime.timedelta(minutes=APPOINTMENT_BUFFER_TIME)
    return start_time, end_time, slot_duration, buff_time


def exclude_booked_slots(appointments, slots, slot_duration=None):
    """Exclude the booked slots from the given list of slots.

    :param appointments: The appointments to exclude.
    :param slots: The slots to exclude the appointments from.
    :param slot_duration: The duration of each slot.
    :return: The slots with the booked slots excluded.
    """
    available_slots = []
    for slot in slots:
        slot_end = slot + slot_duration
        is_available = True
        for appointment in appointments:
            appointment_start_time = appointment.get_start_time()
            appointment_end_time = appointment.get_end_time()
            if appointment_start_time < slot_end and slot < appointment_end_time:
                is_available = False
                break
        if is_available:
            available_slots.append(slot)
    return available_slots


def get_weekday_num_from_date(date: datetime.date = None) -> int:
    """Get the number of the weekday from the given date."""
    if date is None:
        date = datetime.date.today()
    return get_weekday_num(date.strftime("%A"))


def is_working_day(staff_member: StaffMember, day: int) -> bool:
    """Check if the given day is a working day for the staff member."""
    working_days = list(WorkingHours.objects.filter(staff_member=staff_member).values_list('day_of_week', flat=True))
    return day in working_days


def get_staff_member_start_time(staff_member: StaffMember, date: datetime.date) -> Optional[datetime.time]:
    """Return the start time for the given staff member on the given date."""
    weekday_num = get_weekday_num_from_date(date)
    working_hours = get_working_hours_for_staff_and_day(staff_member, weekday_num)
    return working_hours['start_time']


def get_staff_member_buffer_time(staff_member: StaffMember, date: datetime.date) -> float:
    """Return the buffer time for the given staff member on the given date."""
    _, _, _, buff_time = get_times_from_config(date)
    buffer_minutes = buff_time.total_seconds() / 60
    return staff_member.appointment_buffer_time or buffer_minutes


def get_staff_member_end_time(staff_member: StaffMember, date: datetime.date) -> Optional[datetime.time]:
    """Return the end time for the given staff member on the given date."""
    weekday_num = get_weekday_num_from_date(date)
    working_hours = get_working_hours_for_staff_and_day(staff_member, weekday_num)
    return working_hours['end_time']


def get_staff_member_slot_duration(staff_member: StaffMember, date: datetime.date) -> int:
    """Return the slot duration for the given staff member on the given date."""
    _, _, slot_duration, _ = get_times_from_config(date)
    slot_minutes = slot_duration.total_seconds() / 60
    return staff_member.slot_duration or slot_minutes


def get_appointments_for_date_and_time(date, start_time, end_time, staff_member):
    """Returns all appointments that overlap with the specified date and time range.

    :param date: The date to filter appointments on.
    :param start_time: The starting time to filter appointments on.
    :param end_time: The ending time to filter appointments on.
    :param staff_member: The staff member to filter appointments on.

    :return: QuerySet, all appointments that overlap with the specified date and time range
    """
    return Appointment.objects.filter(
            appointment_request__date=date,
            appointment_request__start_time__lte=end_time,
            appointment_request__end_time__gte=start_time,
            appointment_request__staff_member=staff_member
    )


def calculate_staff_slots(date, staff_member):
    """Calculate the available slots for the given staff member on the given date.

    :param date: The date to calculate the slots for.
    :param staff_member: The staff member to calculate the slots for.
    :return: A list of available slots.
    """
    # Convert the times to datetime objects
    weekday_num = get_weekday_num_from_date(date)
    if not is_working_day(staff_member, weekday_num):
        return []
    staff_member_start_time = get_staff_member_start_time(staff_member, date)
    start_time = datetime.datetime.combine(date, staff_member_start_time)
    end_time = datetime.datetime.combine(date, get_staff_member_end_time(staff_member, date))

    # Convert the buffer duration in minutes to a timedelta object
    buffer_duration_minutes = get_staff_member_buffer_time(staff_member, date)
    buffer_duration = datetime.timedelta(minutes=buffer_duration_minutes)
    buffer_time_init = datetime.datetime.combine(date, staff_member_start_time)
    buffer_time = buffer_time_init + buffer_duration

    # Convert slot duration to a timedelta object
    slot_duration_minutes = get_staff_member_slot_duration(staff_member, date)
    slot_duration = datetime.timedelta(minutes=slot_duration_minutes)

    return calculate_slots(start_time, end_time, buffer_time, slot_duration)


def get_working_hours_for_staff_and_day(staff_member, day_of_week):
    """Get the working hours for the given staff member and day of the week.

    :param staff_member: The staff member to get the working hours for.
    :param day_of_week: The day of the week to get the working hours for.
    :return: The working hours for the given staff member and day of the week.
    """
    working_hours = WorkingHours.objects.filter(staff_member=staff_member, day_of_week=day_of_week).first()
    start_time = staff_member.get_lead_time()
    end_time = staff_member.get_finish_time()
    if not working_hours and not (start_time and end_time):
        return None
    # If no specific working hours are set for that day, use the default start and end times from StaffMember
    if not working_hours:
        return {
            'staff_member': staff_member,
            'day_of_week': day_of_week,
            'start_time': staff_member.get_lead_time(),
            'end_time': staff_member.get_finish_time()
        }

    # If a WorkingHours instance is found, convert it to a dictionary for consistent return type
    return {
        'staff_member': working_hours.staff_member,
        'day_of_week': working_hours.day_of_week,
        'start_time': working_hours.start_time,
        'end_time': working_hours.end_time
    }



def get_config():
    """Returns the configuration object from the database or the cache."""
    config = cache.get('config')
    if not config:
        config = Config.objects.first()
        # Cache the configuration for 1 hour (3600 seconds)
        cache.set('config', config, 3600)
    return config