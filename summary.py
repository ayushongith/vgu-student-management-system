import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_project.settings')
django.setup()

from django.apps import apps
from django.urls import get_resolver

print("=== APPS & MODELS ===")
for app in apps.get_app_configs():
    if not app.name.startswith('django.') and not app.name.startswith('rest_framework') and not app.name.startswith('corsheaders') and not app.name.startswith('drf_yasg'):
        print(f"App: {app.name}")
        for model in app.get_models():
            print(f"  - Model: {model.__name__}")

print("\n=== URLS ===")
resolver = get_resolver()
for url in resolver.url_patterns:
    if hasattr(url, 'url_patterns'):
        print(f"Path: {url.pattern}")
        for sub_url in url.url_patterns:
            print(f"  - {sub_url.name}: {sub_url.pattern}")
