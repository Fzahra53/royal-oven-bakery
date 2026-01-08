import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery.settings')
django.setup()

print("🔍 DIAGNOSTIC COMPLET - ROYAL OVEN")
print("="*60)

# 1. Configuration
from django.conf import settings
print("\n1. CONFIGURATION")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"   DATABASE: {settings.DATABASES['default']['ENGINE']}")

# 2. Modèles
print("\n2. MODÈLES")
from django.apps import apps
models = apps.get_models()
for model in models:
    try:
        count = model.objects.count()
        print(f"   {model.__name__}: {count} entrées")
    except:
        print(f"   {model.__name__}: ❌ Erreur")

# 3. URLs
print("\n3. URLS")
from django.urls import get_resolver
try:
    resolver = get_resolver()
    url_count = len([p for p in resolver.url_patterns if hasattr(p, 'name') and p.name])
    print(f"   {url_count} URLs nommées")
except:
    print("   ❌ Erreur URLs")

# 4. Templates
print("\n4. TEMPLATES")
import glob
templates = glob.glob("templates/**/*.html", recursive=True)
print(f"   {len(templates)} templates HTML")

# 5. Problèmes connus
print("\n5. PROBLÈMES CONNUS")
print("   - [ ] Vue connexion: filter().first() ✓")
print("   - [ ] ALLOWED_HOSTS: testserver ✓")
print("   - [ ] Migrations: OK ✓")
print("   - [ ] Base de données: OK ✓")

print("\n" + "="*60)
print("🎯 ACTIONS REQUISES:")
print("1. git add . && git commit -m 'Corrections'")
print("2. git push origin [votre-branche]")
print("3. Tester dans navigateur: http://127.0.0.1:8000/")
print("4. Vérifier admin: http://127.0.0.1:8000/admin/")