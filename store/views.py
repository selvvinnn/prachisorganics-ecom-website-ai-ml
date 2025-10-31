import razorpay
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Category,
    Product,
    ComboDeal,
    Review,
    Cart,
    CartItem,
    Order,
    OrderItem,
    ContactMessage,
    CustomUser,
)


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != password2:
            messages.error(request, 'Passwords do not match.')
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = CustomUser.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('store:home')
    return render(request, 'store/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or reverse('store:home')
            return redirect(next_url)
        messages.error(request, 'Invalid credentials.')
    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('store:home')


def home_view(request):
    featured_products = Product.objects.filter(is_available=True)[:4]
    combos = ComboDeal.objects.all()[:4]
    categories = Category.objects.all()
    recent_reviews = Review.objects.select_related('product', 'user').order_by('-created_at')[:10]
    return render(request, 'store/index.html', {
        'featured_products': featured_products,
        'combos': combos,
        'categories': categories,
        'steps': [1, 2, 3, 4],
        'recent_reviews': recent_reviews,
    })


def about_us_view(request):
    return render(request, 'store/about.html')

def terms_view(request):
    return render(request, 'store/terms.html')

def returns_view(request):
    return render(request, 'store/returns.html')

def privacy_view(request):
    return render(request, 'store/privacy.html')

def refund_view(request):
    return render(request, 'store/refund.html')

def faq_view(request):
    return render(request, 'store/faq.html')

def track_order_view(request):
    order = None
    order_id = str(request.GET.get('order_id', '')).strip()
    if order_id.isdigit():
        order = (
            Order.objects
            .select_related('user')
            .prefetch_related('items')
            .filter(id=int(order_id))
            .first()
        )
    return render(request, 'store/track_order.html', { 'order': order })


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)
            messages.success(request, 'Thanks for contacting us! We will reply soon.')
            return redirect('store:contact')
        messages.error(request, 'Please fill in all required fields.')
    return render(request, 'store/contact.html')


def product_list_view(request):
    # Prepare reviews visibility per moderation setting
    site_cfg = None
    try:
        from .models import SiteSettings
        site_cfg = SiteSettings.objects.first()
    except Exception:
        site_cfg = None

    from django.db.models import Prefetch
    reviews_qs = Review.objects.select_related('user')
    if site_cfg and site_cfg.require_review_moderation:
        reviews_qs = reviews_qs.filter(is_approved=True)

    products = Product.objects.filter(is_available=True).prefetch_related(
        Prefetch('reviews', queryset=reviews_qs.order_by('-created_at'), to_attr='visible_reviews')
    )
    category_slug = request.GET.get('category')
    concern = request.GET.get('concern')
    query = request.GET.get('q', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if concern:
        products = products.filter(concern=concern)
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
        # If exactly one result, redirect to product detail
        prod_count = products.count()
        if prod_count == 1:
            only = products.first()
            return redirect('store:product_detail', product_slug=only.slug)
    categories = Category.objects.all()
    return render(request, 'store/products.html', {
        'products': products,
        'categories': categories,
        'active_category': category_slug or '',
        'active_concern': concern or '',
        'query': query,
    })


def product_detail_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    # Only show approved reviews if moderation is enabled
    site_cfg = None
    try:
        from .models import SiteSettings
        site_cfg = SiteSettings.objects.first()
    except Exception:
        site_cfg = None
    reviews_qs = product.reviews.select_related('user')
    if site_cfg and site_cfg.require_review_moderation:
        reviews_qs = reviews_qs.filter(is_approved=True)
    reviews = reviews_qs.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_to_cart':
            return add_to_cart(request, product_slug)
        elif action == 'add_review' and request.user.is_authenticated:
            rating = int(request.POST.get('rating', '0'))
            comment = request.POST.get('comment', '').strip()
            photo = request.FILES.get('photo')
            if 1 <= rating <= 5 and comment:
                is_approved = True
                if site_cfg and site_cfg.require_review_moderation:
                    is_approved = False
                Review.objects.create(
                    product=product,
                    user=request.user,
                    rating=rating,
                    comment=comment,
                    is_approved=is_approved,
                    photo=photo,
                )
                if is_approved:
                    messages.success(request, 'Review submitted!')
                else:
                    messages.success(request, 'Review submitted and pending approval.')
                return redirect('store:product_detail', product_slug=product.slug)
            messages.error(request, 'Please provide a rating (1-5) and a comment.')

    # Calculate review statistics
    total_reviews = reviews.count()
    avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        rating_dist[i] = reviews.filter(rating=i).count()
    
    return render(request, 'store/product_detail.html', {
        'product': product,
        'reviews': reviews[:6],  # Show only first 6 reviews
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_dist': rating_dist,
    })


def combo_deals_view(request):
    # Fetch combos with included products and recent reviews aggregated from products
    from django.db.models import Prefetch, Avg, Count
    site_cfg = None
    try:
        from .models import SiteSettings
        site_cfg = SiteSettings.objects.first()
    except Exception:
        site_cfg = None

    reviews_qs = Review.objects.select_related('user').order_by('-created_at')
    if site_cfg and site_cfg.require_review_moderation:
        reviews_qs = reviews_qs.filter(is_approved=True)

    combos = ComboDeal.objects.prefetch_related(
        Prefetch('products__reviews', queryset=reviews_qs, to_attr='combo_visible_reviews')
    ).all()

    # Build lightweight aggregates for template consumption
    combo_meta = {}
    for combo in combos:
        all_reviews = []
    for p in combo.products.all():
        if hasattr(p, 'combo_visible_reviews'):
            all_reviews.extend(p.combo_visible_reviews)

    count_reviews = len(all_reviews)
    if count_reviews:
        avg_rating = sum([r.rating for r in all_reviews]) / count_reviews
        latest = all_reviews[0]
    else:
        avg_rating = 0
        latest = None

    # ✅ Attach data directly to the combo object
    combo.avg_rating = avg_rating
    combo.review_count = count_reviews
    combo.latest_review = latest

    return render(request, 'store/combos.html', {'combos': combos, 'combo_meta': combo_meta})

def combo_detail_view(request, combo_slug):
    combo = get_object_or_404(ComboDeal, slug=combo_slug)
    included_products = combo.products.filter(is_available=True)
    
    # Collect reviews from included products for display
    site_cfg = None
    try:
        from .models import SiteSettings
        site_cfg = SiteSettings.objects.first()
    except Exception:
        site_cfg = None
        site_cfg = None
    reviews_qs = Review.objects.select_related('user').filter(product__in=included_products).order_by('-created_at')
    if site_cfg and site_cfg.require_review_moderation:
        reviews_qs = reviews_qs.filter(is_approved=True)

    if request.method == 'POST':
        if request.user.is_authenticated:
            action = request.POST.get('action')
            if action == 'add_review':
                # Handle combo review submission
                rating = request.POST.get('rating')
                comment = request.POST.get('comment')
                photo = request.FILES.get('photo')
                
                if rating and comment:
                    # Create a review for the first product in the combo (as a proxy for combo review)
                    if included_products.exists():
                        review = Review.objects.create(
                            product=included_products.first(),
                            user=request.user,
                            rating=int(rating),
                            comment=comment,
                            photo=photo,
                            is_approved=not (site_cfg and site_cfg.require_review_moderation)
                        )
                        if site_cfg and site_cfg.require_review_moderation:
                            messages.success(request, 'Review submitted and will be published after moderation.')
                        else:
                            messages.success(request, 'Review added successfully.')
                    else:
                        messages.error(request, 'No products found in this combo.')
                else:
                    messages.error(request, 'Please provide both rating and comment.')
                return redirect('store:combo_detail', combo_slug=combo.slug)
            else:
                # Handle add to cart
                cart, _ = Cart.objects.get_or_create(user=request.user)
                item, created = CartItem.objects.get_or_create(
                    cart=cart, 
                    combo_deal=combo,
                    defaults={'quantity': 1}
                )
                if not created:
                    item.quantity += 1
                    item.save()
                messages.success(request, 'Combo added to cart.')
                return redirect('store:cart')
        else:
            messages.error(request, 'Please login to perform this action.')
            return redirect('store:combo_detail', combo_slug=combo.slug)
    
    # Calculate review statistics
    all_reviews = Review.objects.filter(product__in=included_products)
    if site_cfg and site_cfg.require_review_moderation:
        all_reviews = all_reviews.filter(is_approved=True)
    
    total_reviews = all_reviews.count()
    avg_rating = all_reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0
    
    # Rating distribution
    rating_dist = {}
    for i in range(1, 6):
        rating_dist[i] = all_reviews.filter(rating=i).count()
    
    return render(request, 'store/combo_detail.html', {
        'combo': combo,
        'included_products': included_products,
        'combo_reviews': reviews_qs[:6],
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'rating_dist': rating_dist,
    })

def view_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product', 'combo_deal').all()
        subtotal = sum([item.line_total() for item in items])
    else:
        cart = None
        items = []
        subtotal = 0
    return render(request, 'store/cart.html', {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
    })


@login_required
def add_to_cart(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    quantity = int(request.POST.get('quantity', '1')) if request.method == 'POST' else 1
    if quantity < 1:
        quantity = 1
    cart, _ = Cart.objects.get_or_create(user=request.user)

    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity,
        unit_price=None  # Individual products use their own price
    )
    messages.success(request, f"Added {product.name} to cart.")
    return redirect('store:cart')


from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')  # latest first
    combos = ComboDeal.objects.filter(user=user) if hasattr(ComboDeal, 'user') else None

    context = {
        "user": user,
        "orders": orders,
        "combos": combos,
    }
    return render(request, "store/profile.html", context)

from django.conf import settings
import razorpay
@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product').all()
    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('store:products')

    subtotal = sum([item.line_total() for item in items]) if items else 0

    if request.method == 'POST':
        
        # 🟢 Save checkout data into session
        request.session['checkout_data'] = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'address': request.POST.get('address'),
            'zipcode': request.POST.get('zipcode'),
            'city': request.POST.get('city'),
        }
        return redirect('store:checkout')
    # 🟢 Create Razorpay Order only on GET (page load)
    if request.method == 'GET':
        client = razorpay.Client(auth=(settings.RP_KEY_ID, settings.RP_KEY_SECRET))
        payment = client.order.create({
            'amount': int(subtotal * 100),  # convert rupees to paise
            'currency': 'INR',
            'payment_capture': 1
        })
        cart.razorpay_order_id = payment['id']
        cart.save()

        context = {
            'cart': cart,
            'payment': payment,
            'items': items,
            'subtotal': subtotal
        }
        return render(request, 'store/checkout.html', context)

    # 🟢 Verify Razorpay payment and redirect to success
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            client = razorpay.Client(auth=(settings.RP_KEY_ID, settings.RP_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': data['razorpay_order_id'],
                'razorpay_payment_id': data['razorpay_payment_id'],
                'razorpay_signature': data['razorpay_signature']
            })

            # ✅ Payment verified — clear cart and redirect to success
            cart.items.all().delete()
            messages.success(request, "Payment successful! Order placed.")
            return JsonResponse({'status': 'success', 'redirect_url': '/order-success/'})

        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)})

    return JsonResponse({'status': 'failure', 'message': 'Invalid request'})

@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()  # remove item if qty goes below 1
    return redirect('store:cart')
    


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        item.delete()
    return redirect('store:cart')

from django.conf import settings

@login_required
def payment_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.select_related('product', 'combo_deal').all()
    checkout_data = request.session.get('checkout_data')
    if not checkout_data or not items:
        messages.error(request, 'Checkout session expired.')
        return redirect('store:checkout')

    # Placeholder payment step. In real integration, redirect to gateway and verify webhook/callback.
    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            first_name=checkout_data['first_name'],
            last_name=checkout_data['last_name'],
            email=checkout_data['email'],
            address=checkout_data['address'],
            zipcode=checkout_data['zipcode'],
            city=checkout_data['city'],
            paid_amount=sum([i.line_total() for i in items]),
            status='processing',
        )
        for item in items:
            if item.combo_deal:
                # For combo deals, create order item with combo reference
                OrderItem.objects.create(
                    order=order,
                    combo_deal=item.combo_deal,
                    price=item.combo_deal.discounted_price,
                    quantity=item.quantity,
                )
                # Reduce stock for all products in the combo
                for product in item.combo_deal.products.all():
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        product.save()
            else:
                # For individual products
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=(item.unit_price if item.unit_price is not None else item.product.get_display_price()),
                    quantity=item.quantity,
                )
                # reduce stock
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity
                    item.product.save()
        # clear cart
        cart.items.all().delete()
        messages.success(request, 'Payment successful! Order placed.')
        request.session.pop('checkout_data', None)
        return redirect('store:home')
    

    subtotal = sum([i.line_total() for i in items])
    return render(request, 'store/payment.html', {
        'items': items,
        'subtotal': subtotal,
        'checkout': checkout_data,
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

@csrf_exempt
@login_required
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RP_KEY_ID, settings.RP_KEY_SECRET))

        try:
            # 1️⃣ Verify payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # 2️⃣ Fetch cart and checkout data
            cart = Cart.objects.get(user=request.user)
            items = cart.items.select_related('product', 'combo_deal').all()
            checkout_data = request.session.get('checkout_data')

            # 3️⃣ Create the Order
            order = Order.objects.create(
                user=request.user,
                first_name=checkout_data.get('first_name'),
                last_name=checkout_data.get('last_name'),
                email=checkout_data.get('email'),
                address=checkout_data.get('address'),
                zipcode=checkout_data.get('zipcode'),
                city=checkout_data.get('city'),
                paid_amount=sum([i.line_total() for i in items]),
                status='processing',
                razorpay_order_id=razorpay_order_id
            )

            # 4️⃣ Transfer cart items → order items
            for item in items:
                if item.combo_deal:
                    OrderItem.objects.create(
                        order=order,
                        combo_deal=item.combo_deal,
                        price=item.combo_deal.discounted_price,
                        quantity=item.quantity,
                    )
                    for product in item.combo_deal.products.all():
                        product.stock = max(product.stock - item.quantity, 0)
                        product.save()
                else:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.unit_price or item.product.get_display_price(),
                        quantity=item.quantity,
                    )
                    item.product.stock = max(item.product.stock - item.quantity, 0)
                    item.product.save()

            # 5️⃣ Clear the cart
            cart.items.all().delete()
            cart.is_paid = True
            cart.save()
            request.session.pop('checkout_data', None)

            return JsonResponse({'status': 'success', 'order_id': order.id})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'status': 'failure', 'message': 'Invalid signature'})
        except Exception as e:
            return JsonResponse({'status': 'failure', 'message': str(e)})

    return JsonResponse({'status': 'failure', 'message': 'Invalid request'})



