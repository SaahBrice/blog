from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Sum
from django.core.cache import cache
from .utils import get_or_create_avatar

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
    is_manual_writer = models.BooleanField(default=False)


    @property
    def is_eligible_for_suggestions(self):
        settings = SiteSettings.load()
        return (self.is_writer and 
                self.is_verified and 
                self.is_premium and 
                self.article_set.count() >= settings.min_articles_for_suggestions)
    def get_avatar_url(self):
        return get_or_create_avatar(self)

    @property
    def is_writer(self):
        if self.is_manual_writer:
            return True

        settings = SiteSettings.load()
        article_count = self.article_set.count()
        follower_count = self.followers.count()
        
        if article_count >= settings.min_articles_for_writer and follower_count >= settings.min_followers_for_writer:
            total_reactions = sum(
                article.reactions.aggregate(total=Sum('count'))['total'] or 0
                for article in self.article_set.all()
            )
            return total_reactions >= settings.min_reactions_for_writer
        return False
    

    def unread_notifications_count(self):
        return self.notifications.filter(is_read=False).count()

    def __str__(self):
        return self.username


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="My Blog")
    site_logo = models.ImageField(upload_to='site/', null=True, blank=True)
    min_articles_for_writer = models.PositiveIntegerField(default=1)
    min_followers_for_writer = models.PositiveIntegerField(default=1)
    min_reactions_for_writer = models.PositiveIntegerField(default=10)

    min_articles_for_suggestions = models.PositiveIntegerField(default=5)
    max_suggested_users = models.PositiveIntegerField(default=5)
    suggestion_cache_timeout = models.PositiveIntegerField(default=3600)  # 1 hour in seconds


    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SiteSettings, self).save(*args, **kwargs)
        cache.clear()

    @classmethod
    def load(cls):
        if cache.get('site_settings') is None:
            obj, created = cls.objects.get_or_create(pk=1)
            cache.set('site_settings', obj)
        return cache.get('site_settings')