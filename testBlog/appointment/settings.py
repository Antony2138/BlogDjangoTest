from django.conf import settings

APPOINTMENT_BASE_TEMPLATE = getattr(
    settings, "APPOINTMENT_BASE_TEMPLATE", "mainController/layout.html"
)
APPOINTMENT_ADMIN_BASE_TEMPLATE = getattr(
    settings, "APPOINTMENT_ADMIN_BASE_TEMPLATE", "mainController/layout.html"
)
APPOINTMENT_LEAD_TIME = getattr(settings, "APPOINTMENT_LEAD_TIME", (9, 0))
APPOINTMENT_FINISH_TIME = getattr(settings, "APPOINTMENT_FINISH_TIME", (18, 30))
APPOINTMENT_SLOT_DURATION = getattr(settings, "APPOINTMENT_SLOT_DURATION", 30)
APPOINTMENT_BUFFER_TIME = getattr(settings, "APPOINTMENT_BUFFER_TIME", 0)
