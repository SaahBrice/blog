from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('follow', 'New Follower'),
        ('comment', 'Commented on'),
        ('comment_reaction', 'Reacted to your comment on'),
        ('reply', 'Replied to your comment on'),
        ('clap', 'Reacted Clap on your post'),
        ('sad', 'Reacted Sad on your post'),
        ('laugh', 'Reacted Sad on your post'),
        ('mention', 'Mentioned you on'),
    )
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('articles.Comment', on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender} {self.get_notification_type_display()} {self.recipient}"