from django import template

register = template.Library()


@register.filter
def tdc(value: int):
    if value is not None and value and value != '' :
        return '{:,}'.format(int(value))
    else:
        return 0


@register.filter
def clac_discount(price: int, discount: int):
    discount_price = price * (discount / 100)
    return '{:,}'.format(int(price - discount_price))

@register.filter
def clac_tax(price: int, discount: int):
    discount_price = int(price * (discount / 100))
    return '{:,}'.format(discount_price)


@register.filter
def sum(x, y):
    return x + y

