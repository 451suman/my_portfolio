from django import template
from django.utils import timezone
import math

register = template.Library()


@register.filter
def timeago(date):
    """
    Convert a datetime to a human-readable "time ago" format
    """
    if not date:
        return "Never"
    
    now = timezone.now()
    diff = now - date
    
    if diff.days == 0:
        seconds = diff.seconds
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = math.floor(seconds / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            hours = math.floor(seconds / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.days < 30:
        weeks = math.floor(diff.days / 7)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff.days < 365:
        months = math.floor(diff.days / 30)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = math.floor(diff.days / 365)
        return f"{years} year{'s' if years != 1 else ''} ago"
