from django import template
from django.utils.timezone import timedelta, now

register = template.Library()


@register.filter
def ticket_count_response(query):
    query = query.filter(message__is_read_by_server=False).distinct().count()
    return query


@register.filter
def ticket_obj_response(query):
    query = query.filter(message__is_read_by_server=False).distinct().all()
    return query


@register.filter
def ticket_count_request(query):
    query = query.filter(message__is_read_by_client=False).distinct().count()
    return query


@register.filter
def ticket_obj_request(query):
    query = query.filter(message__is_read_by_client=False).distinct().all()
    return query


@register.filter
def orders_count(query):
    return query.filter(is_paid=True, is_active=True, canceled=False,
                        second_date=now() - timedelta(days=1)
        ).count()

@register.filter
def orders_obj(query):
    return query.filter(is_paid=True, is_active=True, canceled=False,
                        second_date=now() - timedelta(days=1)
        ).all()
