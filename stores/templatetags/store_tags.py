from django import template
from django.db.models import Max
from django.utils.timezone import timedelta, now

register = template.Library()


def _get_cached_list(query, attr_name, builder):
    instance = getattr(query, "instance", None)
    if instance is not None:
        cached = getattr(instance, attr_name, None)
        if cached is not None:
            return cached
        result = list(builder(query))
        setattr(instance, attr_name, result)
        return result
    return list(builder(query))


@register.filter
def ticket_obj_response(query):
    return _get_cached_list(
        query,
        "_cached_unread_server_tickets",
        lambda q: q.filter(message__is_read_by_server=False)
        .select_related("user")
        .annotate(last_message_date=Max("message__date"))
        .distinct(),
    )


@register.filter
def ticket_count_response(query):
    return len(ticket_obj_response(query))


@register.filter
def ticket_obj_request(query):
    return _get_cached_list(
        query,
        "_cached_unread_client_tickets",
        lambda q: q.filter(message__is_read_by_client=False)
        .select_related("user")
        .annotate(last_message_date=Max("message__date"))
        .distinct(),
    )


@register.filter
def ticket_count_request(query):
    return len(ticket_obj_request(query))


@register.filter
def orders_obj(query):
    return _get_cached_list(
        query,
        "_cached_recent_paid_orders",
        lambda q: q.filter(
            is_paid=True,
            is_active=True,
            canceled=False,
            second_date=now() - timedelta(days=1),
        ).only("id"),
    )


@register.filter
def orders_count(query):
    return len(orders_obj(query))

