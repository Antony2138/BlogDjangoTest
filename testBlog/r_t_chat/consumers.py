import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

ChatGroup = apps.get_model('r_t_chat', 'ChatGroup')
GroupMessage = apps.get_model('r_t_chat', 'GroupMessage')


class ChatroomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        # add and update
        if self.user not in self.chatroom.user_online.all():
            self.chatroom.user_online.add(self.user)
            self.online_status_update()
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        if self.user in self.chatroom.user_online.all():
            self.chatroom.user_online.remove(self.user)
            self.online_status_update()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json['body']

        if not body:
            return
        else:
            message = GroupMessage.objects.create(
                body=body,
                author=self.user,
                group=self.chatroom
            )
        event = {
            'type': 'message_handler',
            'message_id': message.id,
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

        both_online = self.chatroom.user_online.count()
        admin_here = False
        if both_online > 1:
            admin_here = True
        if not self.user.is_superuser and not admin_here:
            admin_event = {
                'type': 'notification_handler',
                'message_id': message.id,
                'chatroom_name': self.chatroom_name,
            }
            async_to_sync(self.channel_layer.group_send)(
                "admin_notification", admin_event
            )

    def message_handler(self, event):
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': self.user,
            'chat_group': self.chatroom
        }
        html = render_to_string("partials/chat_p.html", context=context)
        self.send(text_data=html)

    def online_status_update(self):
        event = {
            'type': 'online_handler',
        }
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def online_handler(self, event):
        online_in_chat = self.chatroom.user_online.exclude(id=self.user.id)

        if online_in_chat:
            online_status = True
        else:
            online_status = False

        context = {
            'online_status': online_status
        }

        html = render_to_string("partials/online_status.html", context=context)
        self.send(text_data=html)


class AdminNotificationConsumer(WebsocketConsumer):

    def connect(self):
        self.user = self.scope['user']
        self.group_name = "admin_notification"

        if not self.user.is_superuser:
            return

        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def notification_handler(self, event):
        message_id = event['message_id']
        chatroom_name = event['chatroom_name']
        message = GroupMessage.objects.get(id=message_id)
        context = {
            'message': message,
            'user': message.author,
            'chatroom_name': chatroom_name
        }
        html = render_to_string("partials/admin_notification.html", context=context)
        self.send(text_data=html)
