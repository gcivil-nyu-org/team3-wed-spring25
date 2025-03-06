import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Conversation, ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_name = self.scope['url_route']['kwargs']['conversation_name']
        self.room_group_name = self.conversation_name
        
        # Debug: log connection attempt
        print(f"Attempting to connect to conversation: {self.room_group_name}")
        
        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        sender_id = data.get('sender_id')
        conversation_id = data.get('conversation_id')

        # Use sync_to_async wrapped methods for database queries
        sender = await self._get_user(sender_id)
        conversation = await self._get_conversation(conversation_id)
        
        if sender and conversation:
            # It's recommended to wrap the DB write as well
            await self._create_chat_message(conversation, sender, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id
        }))

    @sync_to_async
    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def _get_conversation(self, conv_id):
        try:
            return Conversation.objects.get(pk=conv_id)
        except Conversation.DoesNotExist:
            return None

    @sync_to_async
    def _create_chat_message(self, conversation, sender, message):
        return ChatMessage.objects.create(
            conversation=conversation,
            sender=sender,
            content=message
        )
