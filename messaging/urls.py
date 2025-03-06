from django.urls import path
from . import views

urlpatterns = [
    # Landing page for the chat interface
    path('', views.chat_home, name='chat_home'),
    
    # Endpoint to get or create a conversation between users
    path('get_or_create_conversation/', views.get_or_create_conversation, name='get_or_create_conversation'),
    
    # Endpoint to fetch conversation messages
    path('conversation_messages/<int:conversation_id>/', views.conversation_messages, name='conversation_messages'),
]
