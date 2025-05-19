from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string


def search_users_to_admin_chats(query, type_user=""):
    if type_user == "staff":
        users = get_user_model().objects.filter(is_staff=True)
    elif type_user == "client":
        users = get_user_model().objects.filter(is_staff=False)
    else:
        users = get_user_model().objects.none()
    users = users.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(is_superuser=True)
    html = render_to_string("partials/user_group_list.html", {"page_obj": users})
    response = HttpResponse(html)
    return response
