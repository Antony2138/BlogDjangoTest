from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import (Http404, HttpResponse, HttpResponseBadRequest,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import require_superuser
from .forms import ChatmessageCreateForm
from .models import ChatGroup
from .services import search_users_to_admin_chats


@login_required
@require_superuser
def admin_chat(request):
    """Страница администратора со списком всех пользователей"""
    return render(request, "admin_list_of_chats.html")


@login_required
@require_superuser
def paginate_clients_chat(request):
    clients = get_user_model().objects.filter(is_staff=False)
    page_number = request.GET.get("page", 1)
    paginator = Paginator(clients, 8)
    page_obj = paginator.get_page(page_number)
    if request.htmx:
        return render(request, "partials/client_list.html", {"page_obj": page_obj})

    return JsonResponse({'error': 'HTMX only'}, status=400)


@login_required
@require_superuser
def search_chat_clients(request):
    query = request.GET.get("q", "").strip()
    if query == "":
        response = HttpResponse(status=204)
        response['HX-Trigger'] = "paginate-client"
        return response

    return search_users_to_admin_chats(query, "client")


@login_required
@require_superuser
def paginate_staff_chat(request):
    staffs = get_user_model().objects.filter(is_staff=True).exclude(is_superuser=True)
    page_number = request.GET.get("page", 1)
    paginator = Paginator(staffs, 8)
    page_obj = paginator.get_page(page_number)

    if request.htmx:
        return render(request, "partials/staff_chat_list.html", {"page_obj": page_obj})

    return JsonResponse({'error': 'HTMX only'}, status=400)


@login_required
@require_superuser
def search_chat_staff(request):
    query = request.GET.get("q", "").strip()
    if query == "":
        response = HttpResponse(status=204)
        response['HX-Trigger'] = "paginate-staff"
        return response

    return search_users_to_admin_chats(query, "staff")


@login_required
def get_or_create_chatroom(request):
    other_user = get_user_model().objects.filter(is_superuser=True).first()

    chat = ChatGroup.objects.filter(
        is_private=True,
        members=request.user
    ).filter(members=other_user).first()

    if chat:
        return redirect('chatroom', chat.group_name)

    chat = ChatGroup.objects.create(is_private=True)
    chat.members.add(request.user, other_user)
    chat.save()

    return redirect('chatroom', chat.group_name)


@login_required
@require_superuser
def get_or_create_chatroom_from_chat_admin(request, user_id):

    if not user_id:
        return HttpResponseBadRequest("No client_id provided.")

    chat_admin_user = get_user_model().objects.filter(is_superuser=True, is_staff=True).first()
    user = get_object_or_404(get_user_model(), id=user_id)

    if not request.user == chat_admin_user:
        return HttpResponseBadRequest("No access.")
    chat = ChatGroup.objects.filter(
        is_private=True,
        members=user
    ).filter(members=chat_admin_user).first()

    if chat:
        return redirect('chatroom', chat.group_name)

    chat = ChatGroup.objects.create(is_private=True)
    chat.members.add(request.user, user)
    chat.save()

    return redirect('chatroom', chat.group_name)


@login_required
def chat_view(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
    chat_messages = chat_group.groupmessage_set.all().order_by("created")
    form = ChatmessageCreateForm()

    if request.user in chat_group.members.all():
        other_user = chat_group.members.exclude(id=request.user.id).first()
    else:
        raise Http404()

    # if request.htmx:
    #     form = ChatmessageCreateForm(request.POST)
    #     if form.is_valid():
    #         message = form.save(commit=False)
    #         message.author = request.user
    #         message.group = chat_group
    #         message.save()
    #         context = {
    #             'message': message,
    #             'user': request.user
    #         }
    #         return render(request, "partials/chat_p.html", context)

    context = {
        'chat_messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
        'chat_group': chat_group
    }
    return render(request, "chat.html", context=context)


@login_required
@require_superuser
def load_chatroom_from_push(request, chatroom_name):
    if chatroom_name and request.htmx:
        chatroom = get_object_or_404(ChatGroup, group_name=chatroom_name, is_private=True)
        other_user = chatroom.members.exclude(id=request.user.id).first()
    else:
        HttpResponseBadRequest("No access.")

    if not other_user:
        return HttpResponseBadRequest("No access.")

    return render(request, "admin_list_of_chats.html", {"other_user": other_user, "load_from_push": True})
