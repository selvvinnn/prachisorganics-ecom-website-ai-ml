# store/utils.py
from django.conf import settings
from .models import Cart

def get_or_create_cart(request):
    """
    DB-backed cart:
    - If user is authenticated, prefer user-linked cart (one active cart per user).
    - Otherwise, store cart_id in session.
    """
    # Try user cart first
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user, defaults={})
        request.session['cart_id'] = cart.id
        return cart

    # For anonymous users, use session-stored cart id
    cart_id = request.session.get('cart_id')
    if cart_id:
        try:
            cart = Cart.objects.get(id=cart_id)
            return cart
        except Cart.DoesNotExist:
            pass

    cart = Cart.objects.create()
    request.session['cart_id'] = cart.id
    return cart
