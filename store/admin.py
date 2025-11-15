from django.contrib import admin
from django.db import models
from .models import (
    Category, Product, ComboDeal, Review, 
    Cart, CartItem, Order, OrderItem, ContactMessage, SiteSettings, Offer, ShippingAddress, CustomUser, Coupon
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'sale_price', 'stock', 'is_available', 'what_makes_it_potent', 'how_to_use', 'ideal_for', 'consumer_studies']
    list_filter = ['category', 'concern', 'is_available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    formfield_overrides = {
        models.TextField: {'widget': admin.widgets.AdminTextareaWidget(attrs={'rows':4, 'cols':80})},   
    }

@admin.register(ComboDeal)
class ComboDealAdmin(admin.ModelAdmin):
    list_display = ['name', 'original_price', 'discounted_price']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    list_editable = ['is_approved']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at']
    list_filter = ['submitted_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'paid_amount', 'status', 'razorpay_order_id', 'razorpay_payment_id', 'created_at')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'user__username', 'email')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_payment_status', 'created_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percentage', 'active', 'valid_from', 'valid_to']
    list_filter = ['active']
    search_fields = ['code']



@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['support_email', 'support_phone']

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'address_line1', 'city', 'state', 'zipcode', 'country', 'phone_number']
    list_filter = ['city', 'state', 'country']