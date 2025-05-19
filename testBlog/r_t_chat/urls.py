from django.urls import path

from .views import (admin_chat, chat_view, get_or_create_chatroom,
                    get_or_create_chatroom_from_chat_admin,
                    load_chatroom_from_push, paginate_clients_chat,
                    paginate_staff_chat, search_chat_clients,
                    search_chat_staff)

urlpatterns = (
    [
        path("admin_chats/", admin_chat, name="admin_chat"),
        path("start_chat_admin/", get_or_create_chatroom, name="start_chat"),
        path("room/<chatroom_name>", chat_view, name="chatroom"),
        path("start_chat_from_admin/<int:user_id>",
             get_or_create_chatroom_from_chat_admin,
             name="start_chat_from_admin"),
        path("load_chatroom_from_push/<chatroom_name>", load_chatroom_from_push, name="load_chatroom_from_push"),
        path("paginate_clients/", paginate_clients_chat, name="paginate_clients"),
        path("admin/chat/search/clients/", search_chat_clients, name="search_chat_clients"),
        path("admin/chat/search/staff/", search_chat_staff, name="search_chat_staff"),

        path("paginate_staff_chat/", paginate_staff_chat, name="paginate_staff_chat"),
    ]
)
