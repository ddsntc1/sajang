import markdown
from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta


register = template.Library()

@register.filter
def sub(value,arg):
    return value - arg

@register.filter
def mark(value):
    extensions = ["nl2br","fenced_code"]
    return mark_safe(markdown.markdown(value,extensions=extensions))


@register.filter
def time_since(value):
    now = timezone.localtime()
    value = timezone.localtime(value)  
    diff = now - value

    # 시간차를 초 단위로 계산
    seconds = diff.total_seconds()
    

    if seconds >= 604800:
        return value.strftime("%Y/%m/%d")
    
    # 1일 이상
    if seconds >= 86400:
        days = int(seconds / 86400)
        return f"{days}일 전"
    
    # 1시간 이상
    if seconds >= 3600 and seconds < 86400:
        return value.strftime("%H:%M")
    # 1분 이상
    if seconds >= 60:
        minutes = int(seconds / 60)
        return f"{minutes}분 전"
    
    # 1분 미만
    return "방금 전"