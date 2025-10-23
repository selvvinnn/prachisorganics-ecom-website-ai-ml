from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_us_view, name='about'),
    path('terms/', views.terms_view, name='terms'),
    path('returns/', views.returns_view, name='returns'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('refund/', views.refund_view, name='refund'),
    path('track_order/', views.track_order_view, name='track_order'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    path('products/', views.product_list_view, name='products'),
    path('products/<slug:product_slug>/', views.product_detail_view, name='product_detail'),
    path('combos/', views.combo_deals_view, name='combos'),
    path('combos/<slug:combo_slug>/', views.combo_detail_view, name='combo_detail'),
    path('cart/', views.view_cart, name='cart'),
    path('cart/add/<slug:product_slug>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/', views.payment_view, name='payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('order-success/', TemplateView.as_view(template_name='store/order_success.html'), name='order_success'),

]



