"""
Production settings overrides for Railway deployment
"""
import os
from .settings import *

# Ensure DEBUG is False in production
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Cloudinary secure URLs
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'dm4pmi9ae'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', '162377819271374'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', 'G8A6ecXrJz-ml1UouH1nwNF4xF0'),
    'SECURE': True,  # Force HTTPS
    'STATICFILES_MANIFEST_ROOT': os.path.join(BASE_DIR, 'manifest'),
}

# Ensure MEDIA_URL is correct
MEDIA_URL = '/media/'

