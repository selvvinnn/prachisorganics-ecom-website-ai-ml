from .models import SiteSettings, Offer, Category, Product
from django.db.models import Sum
from .utils import get_or_create_cart


def cart_count(request):
    try:
        cart = get_or_create_cart(request)
        count = cart.items.aggregate(
            total=Sum('quantity')
        )['total'] or 0
    except Exception:
        count = 0

    return {'cart_count': count}

def site_settings(request):
    settings_obj = None
    try:
        settings_obj = SiteSettings.objects.first()
    except Exception:
        settings_obj = None
    try:
        offers = list(Offer.objects.filter(is_active=True)[:3])
    except Exception:
        offers = []
    try:
        categories = list(Category.objects.all())
    except Exception:
        categories = []
    try:
        face_products = list(Product.objects.filter(category__slug__iexact='skin-care')[:8])
        hair_products = list(Product.objects.filter(category__slug__iexact='hair-care')[:8])
        body_products = list(Product.objects.filter(category__slug__iexact='body-care')[:8])
    except Exception:
        face_products = hair_products = body_products = []
    return {
        'site_settings': settings_obj,
        'header_offers': offers,
        'nav_categories': categories,
        'nav_face_products': face_products,
        'nav_hair_products': hair_products,
        'nav_body_products': body_products,
    }


