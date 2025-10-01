from django import template

register = template.Library()


@register.filter(name='inr')
def inr(value):
    try:
        amount = float(value)
    except Exception:
        return value
    # Simple INR formatting with rupee symbol and two decimals
    return f"₹{amount:,.2f}"


