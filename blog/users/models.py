from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Sum

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by')
    is_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    
    @property
    def is_writer(self):
        article_count = self.article_set.count()
        follower_count = self.followers.count()
        
        if article_count >= 12 and follower_count >= 5:
            total_reactions = sum(
                article.reactions.aggregate(total=Sum('count'))['total'] or 0
                for article in self.article_set.all()
            )
            return total_reactions >= 1000
        return False
    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()
    
    def __str__(self):
        return self.username