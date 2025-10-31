from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import datetime 


class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    shipping_address = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    hover_image = models.ImageField(upload_to='categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    CONCERN_CHOICES = [
        ('acne', 'Acne'),
        ('hair_fall', 'Hair Fall'),
        ('dry_skin', 'Dry Skin'),
        ('aging', 'Anti-Aging'),
        ('hydration', 'Hydration'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    concern = models.CharField(max_length=50, choices=CONCERN_CHOICES, blank=True)
    what_makes_it_potent = models.TextField(blank=True)
    how_to_use = models.TextField(blank=True)
    ideal_for = models.TextField(blank=True)
    consumer_studies = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_display_price(self):
        return self.sale_price if self.sale_price is not None else self.price

    def __str__(self) -> str:
        return self.name




class ComboDeal(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, related_name='combo_deals', blank=True)
    image = models.ImageField(upload_to='combos/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='reviews/', blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.product.name} - {self.rating}"


class Cart(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_signature = models.CharField(max_length=100, blank=True, null=True)
    is_paid = models.BooleanField(default=False)


    def __str__(self) -> str:
        return f"Cart #{self.id} for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    combo_deal = models.ForeignKey(ComboDeal, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def line_total(self):
        if self.combo_deal:
            return self.combo_deal.discounted_price * self.quantity
        elif self.unit_price is not None:
            return self.unit_price * self.quantity
        else:
            return self.product.get_display_price() * self.quantity

    def get_name(self):
        if self.combo_deal:
            return self.combo_deal.name
        return self.product.name

    def get_image(self):
        if self.combo_deal:
            return self.combo_deal.image
        return self.product.image

    def __str__(self) -> str:
        name = self.get_name()
        return f"{name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='orders')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    zipcode = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.user.username}"

#Auto add shipping date when marked as shipped
@receiver(pre_save, sender=Order)
def set_date_shipped(sender, instance, **kwargs):
    if instance.pk:
        now = datetime.datetime.now()
        obj = sender._default_manager.get(pk=instance.pk)
        if instance.shipped and not obj.shipped:
            instance.date_shipped = now

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    combo_deal = models.ForeignKey(ComboDeal, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def line_total(self):
        return self.price * self.quantity

    def get_name(self):
        if self.combo_deal:
            return self.combo_deal.name
        return self.product.name

    def __str__(self) -> str:
        name = self.get_name()
        return f"{name} ({self.quantity})"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.subject}"


class SiteSettings(models.Model):
    brand_tagline = models.CharField(max_length=255, blank=True, default='Nourish your natural beauty with organic, cruelty-free care.')
    support_email = models.EmailField(blank=True, null=True)
    support_phone = models.CharField(max_length=50, blank=True, default='')
    instagram_url = models.URLField(blank=True, default='')
    facebook_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    youtube_url = models.URLField(blank=True, default='')
    pinterest_url = models.URLField(blank=True, default='')
    require_review_moderation = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self) -> str:
        return 'Site Settings'


class Offer(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=200, blank=True)
    cta_text = models.CharField(max_length=40, blank=True)
    cta_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.title

class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shipping_addresses', blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, null=True, blank=True)
    zipcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    #Don't pluralize address
    class Meta:
        verbose_name_plural = 'Shipping Address'

    def __str__(self):
        return f'Shipping Address - {str(self.id)}'
