# messaging/models.py

from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """A conversation between exactly two users."""

    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_initiated"
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations_received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {self.user1.username} and {self.user2.username}"

    def get_participants(self):
        return [self.user1, self.user2]

    def get_conversation_name(self):
        """
        We'll use this to form a unique WebSocket group name.
        For example: 'chat_3_5' if user1's id=3 and user2's id=5
        """
        user_ids = sorted([self.user1.id, self.user2.id])
        return f"chat_{user_ids[0]}_{user_ids[1]}"


class ChatMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.conversation}"
