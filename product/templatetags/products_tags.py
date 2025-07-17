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


@register.filter
def active_category(orm):
    if orm and orm.exists():
        try:
            return orm.filter(is_active=True).order_by('-sort_number').all()
        except Exception as e:
            return orm.filter(is_active=True).all()
    else:
        return None

@register.filter
def sort_number(orm):
    if orm and orm.exists():
        try:
            return orm.order_by('-sort_number').all()
        except Exception as e:
            return orm.all()
    else:
        return None
