from django import template
from django.conf import settings

register = template.Library()

@register.filter
def cloudinary_url(image_field):
    """Ensure Cloudinary URLs are properly formatted with HTTPS"""
    if not image_field:
        return ''
    url = str(image_field.url)
    # Ensure HTTPS for Cloudinary URLs
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    return url

@register.simple_tag
def static_image(path):
    """Helper tag for static images"""
    return f"/static/{path.lstrip('/')}"

