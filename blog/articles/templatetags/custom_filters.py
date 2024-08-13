from datetime import datetime, timedelta, timezone
import json
from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import is_aware, make_aware, get_current_timezone


register = template.Library()

@register.filter(name='get_first_paragraph')
def get_first_paragraph(content, word_limit=20):
    try:
        content_json = json.loads(content)
        for block in content_json.get('blocks', []):
            if block.get('type') == 'paragraph':
                text = block.get('data', {}).get('text', '')
                words = text.split()
                truncated_text = ' '.join(words[:word_limit])
                if len(truncated_text) > 100:
                    truncated_text = truncated_text[:100] + '...'
                elif len(words) > word_limit:
                    truncated_text += '...'
                return mark_safe(truncated_text)
    except json.JSONDecodeError:
        return ''
    return ''


@register.filter(name='simple_timesince')
def simple_timesince(value):
    now = datetime.now()
    if is_aware(value):
        now = make_aware(now, get_current_timezone())
    elif not is_aware(now):
        value = value.replace(tzinfo=None)
    
    diff = now - value

    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif diff < timedelta(days=30):
        days = diff.days
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(diff.days / 365)
        return f'{years} year{"s" if years > 1 else ""} ago'