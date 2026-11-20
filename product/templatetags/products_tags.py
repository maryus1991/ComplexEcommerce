from django import template

register = template.Library()


@register.filter
def tdc(value: int):
    if value is not None and value and value != "":
        return "{:,}".format(int(value))
    else:
        return 0


@register.filter
def clac_discount(price: int, discount: int):
    discount_price = price * (discount / 100)
    return "{:,}".format(int(price - discount_price))


@register.filter
def clac_tax(price: int, discount: int):
    discount_price = int(price * (discount / 100))
    return "{:,}".format(discount_price)


@register.filter
def clac_tax_no_format(price: int, discount: int):
    discount_price = int(price * (discount / 100))
    return discount_price


@register.filter
def sum(x, y):
    try:
        x = int(x)
    except Exception:
        x = 0

    try:
        y = int(y)
    except Exception:
        y = 0


    return "{:,}".format(int(x) + int(y))


@register.filter
def mines(x, y):
    if x > y:
        return "{:,}".format(int(x) - int(y))
    else:
        return "{:,}".format(int(y) - int(x))


@register.filter
def tdcR(value: int):
    if value is not None and value and value != "":
        return "{:,}".format(int(value) * 10)
    else:
        return 0


@register.filter
def clac_tax_no_format_R(price: int, discount: int):
    discount_price = int(price * (discount / 100)) * 10
    return discount_price


@register.filter
def sumR(x, y):
    return "{:,}".format((int(x) + int(y)) * 10)


@register.filter
def minesR(x, y):
    if x > y:
        return "{:,}".format((int(x) - int(y)) * 10)
    else:
        return "{:,}".format((int(y) - int(x)) * 10)


@register.filter
def order_by(orm, sort):
    return orm.order_by(sort)


def _get_prefetched_items(orm):
    instance = getattr(orm, "instance", None)
    rel = getattr(orm, "rel", None)
    if instance is not None and rel is not None:
        cache_name = rel.get_cache_name()
        prefetched = getattr(instance, "_prefetched_objects_cache", None)
        if prefetched and cache_name in prefetched:
            return prefetched[cache_name]
    return None


@register.filter
def active_category(orm):
    if not orm:
        return None
    prefetched = _get_prefetched_items(orm)
    if prefetched is not None:
        active = [obj for obj in prefetched if getattr(obj, "is_active", False)]
        if not active:
            return None
        active.sort(key=lambda obj: getattr(obj, "sort_number", 0), reverse=True)
        return active
    try:
        qs = orm.filter(is_active=True).order_by('-sort_number')
    except Exception:
        qs = orm.filter(is_active=True)
    return qs


@register.filter
def active_product(orm):
    if not orm:
        return None
    qs = orm.filter(
        is_active=True,
        store__is_active=True,
        store__is_verified=True,
        admin_verified=True,
        brand__is_active=True,
        category__is_active=True,
    )
    try:
        return qs.order_by('-sort_number')
    except Exception:
        return qs


@register.filter
def sort_number(orm):
    if not orm:
        return None
    prefetched = _get_prefetched_items(orm)
    if prefetched is not None:
        if not prefetched:
            return None
        return sorted(prefetched, key=lambda obj: getattr(obj, "sort_number", 0), reverse=True)
    try:
        return orm.order_by('-sort_number')
    except Exception:
        return orm.all()

@register.filter
def multiply(x, y):
    return "{:,}".format(int(x) * int(y))


@register.filter
def colleague(product, request):
    return "{:,}".format(product.get_product_price(request=request))

@register.filter
def colleague_header(product):
    return "{:,}".format(product.get_item_price())