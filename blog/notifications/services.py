from .models import Notification
from django.db import transaction

from .onesignal_service import OneSignalService



def create_notification(recipient, notification_type, sender=None, article=None, comment=None, text=None):

    action_verb = {
        'follow': 'followed you',
        'comment': 'commented on your article',
        'comment_reaction': 'reacted to your comment',
        'reply': 'replied to your comment',
        'clap': 'clapped on your article',
        'sad': 'reacted sad to your article',
        'laugh': 'reacted laugh at your article',
        'mention': 'mentioned you in'
    }
    default_text = f"{sender} {action_verb[notification_type]}"
    with transaction.atomic():
        notification = Notification.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            article=article,
            comment=comment,
            text=text or default_text
        )
        onesignal_service = OneSignalService()
        player_ids = [recipient.onesignal_player_id] if recipient.onesignal_player_id else []
        if player_ids:
            onesignal_service.send_notification(
                player_ids,
                text or default_text,
                {'notification_type': notification_type}
            )
    return notification