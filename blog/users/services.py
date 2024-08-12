
from django.core.cache import cache
from django.db import models
from .models import User, SiteSettings
from articles.models import Reaction, Article
from notifications.services import create_notification
from django.db.models import Count, Sum, Q, OuterRef, Subquery







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
        # Get tags from articles the user has interacted with
        user_interactions = Article.objects.filter(
            Q(reactions__user=user) |
            Q(comments__author=user) |
            Q(bookmarks=user)
        ).values_list('tags__name', flat=True).distinct()

        # If user has no interactions, get popular tags
        if not user_interactions:
            user_interactions = Article.objects.values_list('tags__name', flat=True).annotate(
                tag_count=Count('id')
            ).order_by('-tag_count')[:10]

        reaction_subquery = Reaction.objects.filter(
            article__author=OuterRef('pk')
        ).values('article__author').annotate(
            total_reactions=Sum('count')
        ).values('total_reactions')

        suggested_users = User.objects.filter(
            is_manual_writer=True,
            is_verified=True,
            is_premium=True,
            article__tags__name__in=user_interactions
        ).exclude(
            Q(id=user.id) | Q(followers=user)
        ).annotate(
            posts_count=Count('article', filter=Q(article__status='published'), distinct=True),
            followers_count=Count('followers', distinct=True),
            reactions_count=Subquery(reaction_subquery, output_field=models.IntegerField())
        ).filter(
            posts_count__gte=settings.min_articles_for_suggestions
        ).distinct().order_by('-posts_count')[:settings.max_suggested_users]

        cache.set(cache_key, list(suggested_users), settings.suggestion_cache_timeout)

    return suggested_users