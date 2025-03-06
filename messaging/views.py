from django.http import JsonResponse
from .models import Conversation, ChatMessage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render

@login_required
def get_or_create_conversation(request):
    other_user_id = request.GET.get('other_user_id')
    other_user = get_object_or_404(User, pk=other_user_id)

    # Check if conversation already exists
    conversation = (Conversation.objects.filter(
        user1__in=[request.user, other_user],
        user2__in=[request.user, other_user]
    ).first())

    if not conversation:
        # Create a new one
        conversation = Conversation.objects.create(user1=request.user, user2=other_user)

    data = {
        'conversation_id': conversation.id,
        'conversation_name': conversation.get_conversation_name()
    }
    return JsonResponse(data)

@login_required
def conversation_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    # Optional: verify that request.user is one of the participants
    if request.user not in conversation.get_participants():
        return JsonResponse({'error': 'Not allowed'}, status=403)

    messages = conversation.messages.order_by('timestamp')
    data = {
        'messages': [
            {
                'sender_id': msg.sender.id,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat()
            }
            for msg in messages
        ]
    }
    return JsonResponse(data)


@login_required
def chat_home(request):
    # Exclude the current user from the list
    all_users = User.objects.exclude(id=request.user.id)
    return render(request, 'messaging/chat.html', {'all_users': all_users})