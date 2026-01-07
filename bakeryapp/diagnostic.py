#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

def run_diagnostics():
    print("🔍 DIAGNOSTIC DU PROJET ROYAL OVEN")
    print("=" * 50)
    
    # 1. Vérifier les utilisateurs
    print("\n1. UTILISATEURS DANS LA BASE :")
    users = User.objects.all()
    if users:
        for user in users:
            print(f"   - {user.username} ({user.email}) - Staff: {user.is_staff}")
    else:
        print("   ❌ Aucun utilisateur trouvé")
    
    # 2. Vérifier les URLs
    print("\n2. TEST DES URLs :")
    client = Client()
    urls_to_test = [
        ('accueil', '/'),
        ('produits', '/produits/'),
        ('connexion', '/connexion/'),
        ('inscription', '/inscription/'),
    ]
    
    for name, url in urls_to_test:
        try:
            response = client.get(url)
            status = "✅" if response.status_code == 200 else "⚠️ "
            print(f"   {status} {url} ({response.status_code})")
        except Exception as e:
            print(f"   ❌ {url} - ERREUR: {e}")
    
    # 3. Vérifier la base de données
    print("\n3. BASE DE DONNÉES :")
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_version = cursor.fetchone()
            print(f"   ✅ Connecté à MySQL: {db_version[0]}")
    except Exception as e:
        print(f"   ❌ Erreur DB: {e}")
    
    # 4. Vérifier les templates
    print("\n4. TEMPLATES ESSENTIELS :")
    essential_templates = [
        'bakeryapp/base.html',
        'bakeryapp/accueil.html',
        'bakeryapp/connexion.html',
    ]
    
    from django.template.loader import get_template
    for template in essential_templates:
        try:
            get_template(template)
            print(f"   ✅ {template}")
        except:
            print(f"   ❌ {template} (manquant)")
    
    print("\n" + "=" * 50)
    print("📋 RECOMMANDATIONS :")
    print("1. Redémarrez le serveur: python manage.py runserver")
    print("2. Testez dans le navigateur: http://127.0.0.1:8000/")
    print("3. Pour l'admin: http://127.0.0.1:8000/admin/")
    print("4. Créez un superuser si besoin: python manage.py createsuperuser")

if __name__ == '__main__':
    run_diagnostics()