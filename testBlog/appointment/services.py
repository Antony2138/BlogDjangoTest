import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from .forms import (PersonalInformationForm, ServiceForm, StaffDaysOffForm,
                    StaffWorkingHoursForm)
from .models import Appointment, Service, StaffMember, WorkingHours
from .utils.date_time import convert_12_hour_time_to_24_hour_time
from .utils.db_helpers import (calculate_slots, calculate_staff_slots,
                               day_off_exists_for_date_range,
                               exclude_booked_slots,
                               get_appointments_for_date_and_time,
                               get_staff_member_from_user_id_or_logged_in,
                               get_times_from_config,
                               get_weekday_num_from_date,
                               get_working_hours_for_staff_and_day,
                               working_hours_exist)
from .utils.error_codes import ErrorCode
from .utils.json_context import get_generic_context, json_response


def get_available_slots_for_staff(date, staff_member):
    """Calculate the available time slots for a given date and a staff member.

    :param date: The date for which to calculate the available slots
    :param staff_member: The staff member for which to calculate the available slots
    :return: A list of available time slots as strings in the format '%I:%M %p' like ['10:00 AM', '10:30 AM']
    """

    # Check if the staff member works on the provided date
    day_of_week = (
        get_weekday_num_from_date()
    )  # Python's weekday starts from Monday (0) to Sunday (6)
    working_hours_dict = get_working_hours_for_staff_and_day(staff_member, day_of_week)
    if not working_hours_dict:
        return []

    slot_duration = datetime.timedelta(minutes=staff_member.get_slot_duration())
    slots = calculate_staff_slots(date, staff_member)
    appointments = get_appointments_for_date_and_time(
        date,
        working_hours_dict["start_time"],
        working_hours_dict["end_time"],
        staff_member,
    )
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
    return [slot.strftime("%I:%M %p") for slot in slots]


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
        appointments = Appointment.objects.filter(
            appointment_request__service=service, appointment_request__date=date_
        )
    else:
        appointments = Appointment.objects.filter(appointment_request__date=date_)
    available_slots = get_available_slots(date_, appointments)
    return appointments, available_slots


def prepare_user_profile_data(user, staff_user_id):
    """Prepare the data for the user profile page."""
    staff_member = get_staff_member_from_user_id_or_logged_in(user, staff_user_id)
    bt_help = StaffMember._meta.get_field("appointment_buffer_time")
    bt_help_text = bt_help.help_text

    sd_help = StaffMember._meta.get_field("slot_duration")
    sd_help_text = sd_help.help_text
    service_msg = "Здесь вы можете добавлять/удалять предлагаемые вами услуги, изменяя этот раздел."
    data = {
        "error": False,
        "template": "administration/user_profile.html",
        "extra_context": {
            "superuser": user if user.is_superuser else None,
            "user": staff_member.user if staff_member else user,
            "staff_member": staff_member if staff_member else user,
            "days_off": staff_member.get_days_off().order_by("start_date")
            if staff_member
            else [],
            "working_hours": staff_member.get_working_hours() if staff_member else [],
            "services_offered": staff_member.get_services_offered()
            if staff_member
            else [],
            "staff_member_not_found": not bool(staff_member),
            "buffer_time_help_text": bt_help_text,
            "slot_duration_help_text": sd_help_text,
            "service_msg": service_msg,
        },
    }
    return data


def update_personal_info_service(staff_user_id, post_data, current_user):
    try:
        user = (
            get_user_model().objects.get(pk=staff_user_id)
            if staff_user_id
            else current_user
        )
    except get_user_model().DoesNotExist:
        return None, False, "Пользователь не найден."

    form = PersonalInformationForm(post_data, user=user)
    if form.is_valid():
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.email = form.cleaned_data["email"]
        user.save()
        return user, True, None
    else:
        return None, False, "Заполните все поля"


def handle_entity_management_request(
    request,
    staff_member,
    entity_type,
    instance=None,
    staff_user_id=None,
    instance_id=None,
    add=True,
):
    if not staff_member:
        return json_response(
            "Not authorized",
            status=403,
            success=False,
            error_code=ErrorCode.NOT_AUTHORIZED,
        )

    button_text = "Сохранить" if instance else "Добавить"
    if entity_type == "day_off":
        form = StaffDaysOffForm(instance=instance)
        context = get_working_hours_and_days_off_context(
            request, button_text, "day_off_form", form
        )
        template = "administration/manage_day_off.html"
    else:
        form = StaffWorkingHoursForm(instance=instance)
        context = get_working_hours_and_days_off_context(
            request,
            button_text,
            "working_hours_form",
            form,
            staff_user_id,
            instance,
            instance_id,
        )
        template = "administration/manage_working_hours.html"

    if request.method == "POST" and entity_type == "day_off":
        day_off_form = StaffDaysOffForm(request.POST, instance=instance)
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        if day_off_exists_for_date_range(
            staff_member, start_date, end_date, getattr(instance, "id", None)
        ):
            messages.error(request, "Такие выходные уже установлены")
            redirect_url = reverse(
                "add_day_off", kwargs={"staff_user_id": staff_member.user.id}
            )
            return json_response(custom_data={"redirect_url": redirect_url})
        return handle_day_off_form(day_off_form, staff_member)

    elif request.method == "POST" and entity_type == "working_hours":
        day_of_week = request.POST.get("day_of_week")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        return handle_working_hours_form(
            staff_member, day_of_week, start_time, end_time, add, instance_id
        )

    return render(request, template, context, status=200)


def get_working_hours_and_days_off_context(
    request, btn_txt, form_name, form, user_id=None, instance=None, wh_id=None
):
    """Get the context for the working hours and days off forms.

    :param request: The request object.
    :param btn_txt: The text to display on the submit button.
    :param form_name: The name of the form which depends on if it's a working hours or days off form.
    :param form: The form instance itself.
    :param user_id: The staff user id.
    :param instance: The working hour form instance.
    :param wh_id: The working hour id.
    :return: A dictionary containing the context.
    """
    context = get_generic_context(request)
    context.update(
        {
            "button_text": btn_txt,
            form_name: form,
        }
    )
    if user_id:
        context.update(
            {
                "staff_user_id": user_id,
            }
        )
    if instance:
        context.update(
            {
                "working_hours_instance": instance,
            }
        )
    if wh_id:
        context.update(
            {
                "working_hours_id": wh_id,
            }
        )
    context.update(
        {
            "today": timezone.now(),
        }
    )
    return context


def handle_day_off_form(day_off_form, staff_member):
    """Handle the day off form."""
    if day_off_form.is_valid():
        day_off = day_off_form.save(commit=False)
        day_off.staff_member = staff_member
        day_off.save()
        redirect_url = reverse(
            "user_profile", kwargs={"staff_user_id": staff_member.user.id}
        )
        return json_response(
            "Выходные успешно добавлены", custom_data={"redirect_url": redirect_url}
        )
    else:
        print("check")
        message = "Invalid data:"
        message += get_error_message_in_form(form=day_off_form)
        print(message, "asdasdasd")
        return json_response(
            message, status=400, success=False, error_code=ErrorCode.INVALID_DATA
        )


def get_error_message_in_form(form):
    """
    Get the error message in a form.
    """
    error_messages = []
    for field, errors in form.errors.items():
        error_messages.append(f"{field}: {','.join(errors)}")
    if len(error_messages) == 3:
        return "Empty fields are not allowed."
    return " ".join(error_messages)


def handle_working_hours_form(
    staff_member, day_of_week, start_time, end_time, add, wh_id=None
):
    # Handle the working hours form.

    # Validate inputs
    if not (staff_member and day_of_week and start_time and end_time):
        return json_response(
            "Invalid data.",
            status=400,
            success=False,
            error_code=ErrorCode.INVALID_DATA,
        )

    # Convert start time and end time to 24-hour format
    start_time = convert_12_hour_time_to_24_hour_time(start_time)
    end_time = convert_12_hour_time_to_24_hour_time(end_time)

    # Ensure start time is before end time
    if start_time >= end_time:
        return json_response(
            "Start time must be before end time.",
            status=400,
            success=False,
            error_code=ErrorCode.INVALID_DATA,
        )

    if add:
        # Create new working hours
        if working_hours_exist(day_of_week=day_of_week, staff_member=staff_member):
            return json_response(
                "Выходные уже выбраны.",
                status=400,
                success=False,
                error_code=ErrorCode.WORKING_HOURS_CONFLICT,
            )
        wk = WorkingHours(
            staff_member=staff_member,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
        )
    else:
        # Ensure working_hours_id is provided
        if not wh_id:
            return json_response(
                "Invalid or no working_hours_id provided.",
                status=400,
                success=False,
                error_code=ErrorCode.INVALID_DATA,
            )

        # Get the working hours instance to update
        try:
            wk = WorkingHours.objects.get(pk=wh_id)
            wk.day_of_week = day_of_week
            wk.start_time = start_time
            wk.end_time = end_time
        except WorkingHours.DoesNotExist:
            return json_response(
                "Working hours does not exist.",
                status=400,
                success=False,
                error_code=ErrorCode.WORKING_HOURS_NOT_FOUND,
            )

        # Save working hours
    wk.save()

    # Return success with redirect URL
    redirect_url = (
        reverse("user_profile", kwargs={"staff_user_id": staff_member.user.id})
        if staff_member.user.id
        else reverse("user_profile")
    )
    return json_response(
        "Working hours saved successfully.", custom_data={"redirect_url": redirect_url}
    )
