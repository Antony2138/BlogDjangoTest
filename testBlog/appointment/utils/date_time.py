import datetime
from gettext import ngettext


def combine_date_and_time(date, time) -> datetime.datetime:
    """Combine a date and a time into a datetime object.

    :param date: The date.
    :param time: The time.
    :return: A datetime object.
    """
    return datetime.datetime.combine(date, time)


def get_weekday_num(weekday: str) -> int:
    """Get the number of the weekday.

    :param weekday: The weekday (e.g. "Monday", "Tuesday", etc.)
    :return: The number of the weekday (0 for Sunday, 1 for Monday, etc.)
    """
    weekdays = {
        'monday': 1,
        'tuesday': 2,
        'wednesday': 3,
        'thursday': 4,
        'friday': 5,
        'saturday': 6,
        'sunday': 0
    }
    return weekdays.get(weekday.lower(), -1)


def convert_minutes_in_human_readable_format(minutes: float) -> str:
    """Convert a number of minutes in a human-readable format.

    :param minutes: The number of minutes to convert.
    :return: The converted minutes in a human-readable format.
    """
    if minutes == 0:
        return "Не установлено"
    if minutes < 0:
        raise ValueError("Не может быть отрицательным")
    days, remaining_minutes = divmod(int(minutes), 1440)
    hours, minutes = divmod(int(remaining_minutes), 60)

    parts = []
    if hours:
        hours_display = ngettext("%(count)d час", "%(count)d часа", hours) % {'count': hours}
        parts.append(hours_display)

    if minutes:
        minutes_display = ngettext("%(count)d минут", "%(count)d минут", minutes) % {'count': minutes}
        parts.append(minutes_display)

    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return "{first_part} and {second_part}".format(first_part=parts[0], second_part=parts[1])
    elif len(parts) == 3:
        return "{days}, {hours} and {minutes}".format(days=parts[0], hours=parts[1], minutes=parts[2])


def convert_12_hour_time_to_24_hour_time(time_to_convert) -> str:
    # Convert a 12-hour time to a 24-hour time.
    if isinstance(time_to_convert, (datetime.datetime, datetime.time)):
        return time_to_convert.strftime('%H:%M:%S')
    elif isinstance(time_to_convert, str):
        try:
            time_str = time_to_convert.strip().upper()
            return datetime.datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')
        except ValueError:
            raise ValueError(f"Invalid 12-hour time format: {time_to_convert}")
    else:
        raise ValueError(f"Unsupported data type for time conversion: {type(time_to_convert)}")
