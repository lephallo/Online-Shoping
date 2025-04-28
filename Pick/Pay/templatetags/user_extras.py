from django import template
register = template.Library()

@register.filter
def group_name(user):
    return user.groups.first().name if user.groups.exists() else ''
