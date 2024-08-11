from django import template



register = template.Library()

@register.filter
def get_reaction_count(article, reaction_type):
    return getattr(article, f"{reaction_type}_count")

@register.filter
def get_comment_reaction_count(Comment, reaction_type):
    return getattr(Comment, f"{reaction_type}_count")

@register.filter
def split(value, key):
    return value.split(key)

