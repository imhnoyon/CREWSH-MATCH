from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def subtract_hours(value, hours):
    if isinstance(value, timezone.datetime):
        return value - timedelta(hours=int(hours))
    return value
