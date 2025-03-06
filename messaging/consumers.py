import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_name = self.scope["url_route"]["kwargs"]["conversation_name"]
        self.room_group_name = self.conversation_name

        # Join the chat group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message")
        conversation_id = data.get("conversation_id")

        sender = self.scope["user"]
        # Retrieve the conversation asynchronously
        conversation = await database_sync_to_async(self.get_conversation)(
            conversation_id
        )

        # Determine the recipient by comparing the sender with conversation participants
        if conversation.user1_id == sender.id:
            recipient_id = conversation.user2_id
        else:
            recipient_id = conversation.user1_id

        # Save the new chat message asynchronously
        await database_sync_to_async(ChatMessage.objects.create)(
            conversation=conversation, sender=sender, content=message
        )

        # Broadcast the chat message to the conversation group with sender's id and username
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_id": sender.id,
                "sender_username": sender.username,
            },
        )

        # Retrieve conversation name in a thread-safe way
        conversation_name = await database_sync_to_async(
            conversation.get_conversation_name
        )()
        # Set the link to the general messaging page.
        conversation_link = "/messaging/"

        # Send a notification to the recipient's notifications group with sender's info and the link
        await self.channel_layer.group_send(
            f"notifications_{recipient_id}",
            {
                "type": "send_notification",
                "notification": {
                    "message": message,
                    "sender_id": sender.id,
                    "sender_username": sender.username,
                    "conversation_id": conversation_id,
                    "conversation_name": conversation_name,
                    "link": conversation_link,
                },
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]
        sender_username = event["sender_username"]
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender_id": sender_id,
                    "sender_username": sender_username,
                }
            )
        )

    def get_conversation(self, conversation_id):
        return Conversation.objects.get(id=conversation_id)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_anonymous:
            # Reject connection for anonymous users
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"notifications_{self.user.id}"

            # Join the notifications group for this user
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        notification = event["notification"]
        await self.send(text_data=json.dumps(notification))
