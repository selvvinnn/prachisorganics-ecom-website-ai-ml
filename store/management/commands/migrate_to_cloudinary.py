from django.core.management.base import BaseCommand
from store.models import Product
from cloudinary.uploader import upload

class Command(BaseCommand):
    help = "Migrate existing media files to Cloudinary"

    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            if product.image and not product.image.url.startswith("https://res.cloudinary.com"):
                try:
                    result = upload(product.image.path, folder="products/")
                    product.image = result["secure_url"]
                    product.save()
                    self.stdout.write(self.style.SUCCESS(f"✅ Migrated {product.name}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed {product.name}: {e}"))
        self.stdout.write(self.style.SUCCESS("✅ All products migrated successfully"))
