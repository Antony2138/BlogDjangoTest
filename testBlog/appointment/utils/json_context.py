from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from ..settings import (APPOINTMENT_ADMIN_BASE_TEMPLATE,
                        APPOINTMENT_BASE_TEMPLATE)
from .error_codes import ErrorCode


def get_generic_context(request, admin=True):
    """Get the generic context for the admin pages."""
    return {
        "BASE_TEMPLATE": APPOINTMENT_ADMIN_BASE_TEMPLATE
        if admin
        else APPOINTMENT_BASE_TEMPLATE,
        "user": request.user,
        "is_superuser": request.user.is_superuser,
    }


def json_response(
    message=None, status=200, success=True, custom_data=None, error_code=None, **kwargs
):
    """Return a generic JSON response."""
    response_data = {"message": message, "success": success}
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


def handle_unauthorized_response(request, message, response_type):
    """Handle unauthorized response based on the response type."""
    if response_type == "json":
        return json_response(
            message=message,
            status=403,
            success=False,
            error_code=ErrorCode.NOT_AUTHORIZED,
        )

    # If not 'json', handle as HTML response by default.
    context = {
        "message": message,
        "back_url": reverse("user_profile"),
        "BASE_TEMPLATE": APPOINTMENT_BASE_TEMPLATE,
    }
    # set return code to 403
    return render(
        request, "error_pages/403_forbidden.html", context=context, status=403
    )
