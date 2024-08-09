from .models import User
from django.db.models import Count, Q
from django.core.cache import cache
from .models import User, SiteSettings
from notifications.services import create_notification

def toggle_follow(user, user_to_follow):
    if user == user_to_follow or user.blocked_users.filter(id=user_to_follow.id).exists():
        return False
    if user_to_follow in user.following.all():
        user.following.remove(user_to_follow)
        return False
    else:
        user.following.add(user_to_follow)
        create_notification(user_to_follow, 'follow', sender=user)
        return True

def toggle_block(user, user_to_block):
    if user == user_to_block:
        return False
    if user_to_block in user.blocked_users.all():
        user.blocked_users.remove(user_to_block)
        user.following.add(user_to_block)
        return False
    else:
        user.blocked_users.add(user_to_block)
        user.following.remove(user_to_block)
        user_to_block.following.remove(user)
        return True
    



def get_suggested_users(user):
    settings = SiteSettings.load()
    cache_key = f'suggested_users_{user.id}'
    suggested_users = cache.get(cache_key)

    if suggested_users is None:
        # Get tags the user has interacted with
        user_tags = user.article_set.values_list('tags__name', flat=True).distinct()

        # Query for suggested users
        suggested_users = User.objects.filter(
            is_manual_writer=True,
            is_verified=True,
            is_premium=True,
            article__tags__name__in=user_tags
        ).exclude(
            id=user.id
        ).annotate(
            article_count=Count('article')
        ).filter(
            article_count__gte=settings.min_articles_for_suggestions
        ).distinct().order_by('-article_count')[:settings.max_suggested_users]

        # Cache the results
        cache.set(cache_key, list(suggested_users), settings.suggestion_cache_timeout)

    return suggested_users