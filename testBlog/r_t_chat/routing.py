from django.urls import re_path

from .consumers import AdminNotificationConsumer, ChatroomConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chatroom_name>\w+)/$", ChatroomConsumer.as_asgi()),
    re_path(r"ws/admin-notification/$", AdminNotificationConsumer.as_asgi())
]
