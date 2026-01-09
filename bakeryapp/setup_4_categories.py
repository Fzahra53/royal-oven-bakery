#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bakery.settings')
django.setup()

from bakeryapp.models import Categorie, Produit

def setup_4_categories():
    """Configure les 4 catégories principales"""
    
    print("🔄 Configuration des 4 catégories...")
    
    # 1. Définir les 4 catégories
    categories = [
        {
            "nom": "Viennoiseries",
            "icon": "🥐",
            "description": "Croissants, pains au chocolat, chaussons aux pommes, brioches, pains aux raisins"
        },
        {
            "nom": "Pains", 
            "icon": "🍞",
            "description": "Baguettes traditionnelles, pains complets, pains de campagne, pains aux céréales, pains spéciaux"
        },
        {
            "nom": "Pâtisseries",
            "icon": "🍰", 
            "description": "Gâteaux, tartes aux fruits, éclairs au chocolat, mille-feuilles, macarons, desserts individuels"
        },
        {
            "nom": "Spécialités Maison",
            "icon": "⭐",
            "description": "Créations exclusives, produits de saison, spécialités régionales, produits festifs"
        }
    ]
    
    # 2. Créer/mettre à jour les catégories
    for cat_data in categories:
        cat, created = Categorie.objects.update_or_create(
            nom=cat_data["nom"],
            defaults={
                "description": cat_data["description"]
            }
        )
        status = "créée" if created else "mise à jour"
        print(f"{cat_data['icon']} {cat.nom} - {status}")
    
    # 3. Supprimer les autres catégories
    categories_a_supprimer = Categorie.objects.exclude(
        nom__in=["Viennoiseries", "Pains", "Pâtisseries", "Spécialités Maison"]
    )
    
    for cat in categories_a_supprimer:
        # Transférer produits vers "Pâtisseries"
        cat_patisserie = Categorie.objects.get(nom="Pâtisseries")
        produits = Produit.objects.filter(categorie=cat)
        
        for produit in produits:
            produit.categorie = cat_patisserie
            produit.save()
        
        print(f"🗑️  Supprimé: {cat.nom} ({produits.count()} produits transférés)")
        cat.delete()
    
    # 4. Résumé
    print("\n📊 RÉSUMÉ FINAL:")
    for cat in Categorie.objects.all().order_by('nom'):
        nb_produits = Produit.objects.filter(categorie=cat).count()
        print(f"• {cat.nom}: {nb_produits} produits")
    
    total_produits = Produit.objects.count()
    print(f"\n🎯 Total: {Categorie.objects.count()} catégories, {total_produits} produits")

if __name__ == "__main__":
    setup_4_categories()