#!/usr/bin/env python
import os
import sys

# Ajouter le chemin du projet
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery.settings')

try:
    import django
    django.setup()
    print("✅ Django importé avec succès")
except Exception as e:
    print(f"❌ Erreur Django: {e}")
    sys.exit(1)

print("\n🔍 VÉRIFICATION DU PROJET")
print("=" * 50)

# 1. Vérifier les imports
try:
    from django.contrib.auth.models import User
    from bakeryapp.models import Produit, Categorie, Client
    print("✅ Modèles importés")
except Exception as e:
    print(f"❌ Erreur import modèles: {e}")

# 2. Vérifier la base de données
try:
    user_count = User.objects.count()
    print(f"✅ Base OK - {user_count} utilisateur(s)")
except Exception as e:
    print(f"❌ Erreur base de données: {e}")

# 3. Vérifier les URLs
try:
    from django.urls import reverse, get_resolver
    
    print("\n📋 URLs disponibles:")
    resolver = get_resolver()
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'name') and pattern.name:
            print(f"  - {pattern.name}")
except Exception as e:
    print(f"❌ Erreur URLs: {e}")

# 4. Vérifier les dossiers
print("\n📁 Structure:")
required_dirs = ['static', 'templates', 'media', 'logs']
for dir_name in required_dirs:
    if os.path.exists(dir_name):
        print(f"  ✅ {dir_name}")
    else:
        print(f"  ❌ {dir_name} (manquant)")

print("\n" + "=" * 50)
print("🎉 Projet prêt !")
print("\nProchaines étapes:")
print("1. python manage.py runserver")
print("2. Ouvrez http://127.0.0.1:8000/")
print("3. Pour admin: http://127.0.0.1:8000/admin/")