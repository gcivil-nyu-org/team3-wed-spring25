from .models import Notification
from messaging.models import Message


def notification_count(request):
    """
    Context processor to add unread notification count to all templates.
    """
    if request.user.is_authenticated:
        try:
            # Count unread notifications (get direct SQL count for performance)
            unread_notification_count = Notification.objects.filter(
                recipient=request.user, read=False
            ).count()

            # Count unread messages (also using direct SQL count)
            unread_message_count = (
                Message.objects.filter(recipient=request.user, read=False)
                .exclude(subject="Account Verification Approved")
                .count()
            )

            # Calculate total unread items
            total_unread_count = unread_notification_count + unread_message_count

            # Return all counts
            return {
                "unread_notification_count": unread_notification_count,
                "unread_message_count": unread_message_count,
                "total_unread_count": total_unread_count,
            }
        except Exception:
            # Handle any errors (this ensures our site keeps working)
            return {
                "unread_notification_count": 0,
                "unread_message_count": 0,
                "total_unread_count": 0,
            }

    # Return 0 for all counts for unauthenticated users
    return {
        "unread_notification_count": 0,
        "unread_message_count": 0,
        "total_unread_count": 0,
    }
