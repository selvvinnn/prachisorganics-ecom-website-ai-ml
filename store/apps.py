from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        # Ensure a SiteSettings row exists after migrations
        try:
            from .models import SiteSettings
            if not SiteSettings.objects.exists():
                SiteSettings.objects.create(support_email='support@prachisorganics.com')
        except Exception:
            # App registry might not be ready during migrations
            pass