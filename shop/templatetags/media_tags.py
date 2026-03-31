from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def media_url(value):
    """Если это внешний URL (http:// или https://), возвращаем как есть"""
    if value and (value.startswith('http://') or value.startswith('https://')):
        return value
    return value