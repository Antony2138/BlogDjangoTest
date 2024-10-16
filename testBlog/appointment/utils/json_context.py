from django.http import JsonResponse

from ..settings import APPOINTMENT_ADMIN_BASE_TEMPLATE, APPOINTMENT_BASE_TEMPLATE


def get_generic_context(request, admin=True):
    """Get the generic context for the admin pages."""
    return {
        'BASE_TEMPLATE': APPOINTMENT_ADMIN_BASE_TEMPLATE if admin else APPOINTMENT_BASE_TEMPLATE,
        'user': request.user,
        'is_superuser': request.user.is_superuser,
    }


def json_response(message, status=200, success=True, custom_data=None, error_code=None, **kwargs):
    """Return a generic JSON response."""
    response_data = {
        "message": message,
        "success": success
    }
    if error_code:
        response_data["errorCode"] = error_code.value
    if custom_data:
        response_data.update(custom_data)
    return JsonResponse(response_data, status=status, **kwargs)


def get_generic_context_with_extra(request, extra, admin=True):
    """Get the generic context for the admin pages with extra context."""
    context = get_generic_context(request, admin=admin)
    context.update(extra)
    return context