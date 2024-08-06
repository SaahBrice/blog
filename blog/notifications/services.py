from .models import Notification

def create_notification(recipient, notification_type, sender=None, article=None, comment=None, text=None):
    action_verb = {
        'follow': 'followed you',
        'comment': 'commented on your article',
        'comment_reaction': 'reacted to your comment',
        'reply': 'replied to your comment',
        'clap': 'clapped for your article',
        'sad': 'reacted sad to your article',
        'laugh': 'reacted laugh at your article',
    }
    default_text = f"{sender} {action_verb[notification_type]}"
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notification_type=notification_type,
        article=article,
        comment=comment,
        text=text or default_text
    )