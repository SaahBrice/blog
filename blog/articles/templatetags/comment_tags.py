from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe
import re
from users.models import User


register = template.Library()

@register.filter
def render_mentions(value):
    mention_pattern = r'@(\w+)'
    def replace_mention(match):
        username = match.group(1)
        if username == 'followers':
            return '<span class="mention-followers">@followers</span>'
        user = User.objects.filter(username=username).first()
        if user:
            url = reverse('user_profile', kwargs={'username': username})
            return f'<a href="{url}" class="mention-user">@{username}</a>'
        return f'@{username}'
    
    return mark_safe(re.sub(mention_pattern, replace_mention, value))

@register.filter
def split(value, key):
    return value.split(key)


@register.filter
def get_comment_reaction_count(comment, reaction_type):
    return comment.reactions.filter(reaction_type=reaction_type).count()
