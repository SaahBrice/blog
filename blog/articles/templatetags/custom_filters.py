import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='get_first_paragraph')
def get_first_paragraph(content, word_limit=40):
    try:
        content_json = json.loads(content)
        for block in content_json.get('blocks', []):
            if block.get('type') == 'paragraph':
                text = block.get('data', {}).get('text', '')
                words = text.split()
                truncated_text = ' '.join(words[:word_limit])
                if len(truncated_text) > 300:
                    truncated_text = truncated_text[:297] + '...'
                elif len(words) > word_limit:
                    truncated_text += '...'
                return mark_safe(truncated_text)
    except json.JSONDecodeError:
        return ''
    return ''