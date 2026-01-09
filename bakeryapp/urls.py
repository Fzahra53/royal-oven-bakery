from django.urls import path
from . import views

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('produits/', views.produits, name='produits'),
    path('apropos/', views.apropos, name='apropos'),
    path('contact/', views.contact, name='contact'),

    # Authentification
    path('connexion/', views.connexion_view, name='connexion'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('mon-compte/', views.mon_compte_view, name='mon_compte'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # Panier
    path('mon-panier/', views.mon_panier_view, name='mon_panier'),
    path('panier/ajouter/<int:produit_id>/', views.panier_ajouter, name='panier_ajouter'),
    path('panier/supprimer/<int:produit_id>/', views.panier_supprimer, name='panier_supprimer'),
    path('panier/modifier/<int:produit_id>/', views.panier_modifier_quantite, name='panier_modifier_quantite'),
    path('panier/vider/', views.panier_vider, name='panier_vider'),
    path('debug-panier/', views.debug_panier, name='debug_panier'),

    # Profil et commandes client
    path('mes-commandes/', views.mes_commandes_view, name='mes_commandes'),
    path('commande/<int:pk>/', views.detail_commande_view, name='detail_commande'),
    path('mon-compte/modifier/', views.modifier_profil_view, name='modifier_profil'),

    # Favoris
    path('favoris/', views.mes_favoris, name='mes_favoris'),
    path('favoris/ajouter/<int:produit_id>/', views.ajouter_favori, name='ajouter_favori'),
    path('favoris/retirer/<int:produit_id>/', views.retirer_favori, name='retirer_favori'),

    # Recherche
    path('recherche/', views.recherche, name='recherche'),

    # Avis
    path('produit/<int:produit_id>/avis/', views.ajouter_avis, name='ajouter_avis'),

    # Produits par catégorie et détail
    path('categorie/<int:categorie_id>/', views.produits_par_categorie, name='produits_categorie'),
    path('produit/<int:produit_id>/', views.produit_detail, name='produit_detail'),
    path('backoffice/categories/', views.gestion_categories, name='gestion_categories'),
]


# ---------------- BACKOFFICE ----------------

urlpatterns += [
    # Dashboard
    path("backoffice/", views.backoffice_dashboard, name="backoffice_dashboard"),

    # Produits (CRUD)
    path("backoffice/products/", views.backoffice_products_list, name="backoffice_products_list"),
    path("backoffice/products/new/", views.backoffice_product_create, name="backoffice_product_create"),
    path("backoffice/products/<int:pk>/edit/", views.backoffice_product_update, name="backoffice_product_update"),
    path("backoffice/products/<int:pk>/delete/", views.backoffice_product_delete, name="backoffice_product_delete"),

    # Commandes
    path("backoffice/orders/", views.backoffice_orders_list, name="backoffice_orders_list"),
    path("backoffice/orders/<int:pk>/", views.backoffice_order_detail, name="backoffice_order_detail"),
    path("backoffice/orders/<int:pk>/assign/", views.backoffice_assign_livreur, name="backoffice_assign_livreur"),
    path('commande/<int:commande_id>/facture/', views.generer_facture_pdf, name='generer_facture_pdf'),
    path('categories/', views.gestion_categories_simple, name='categories'),

    # Livreur
    path("delivery/orders/", views.delivery_my_orders, name="delivery_my_orders"),
    path("delivery/orders/<int:pk>/update/", views.delivery_update_status, name="delivery_update_status"),
    path("backoffice/livreurs/", views.backoffice_livreurs_list, name="backoffice_livreurs_list"),
    path("backoffice/livreurs/<int:pk>/toggle/", views.backoffice_livreur_toggle, name="backoffice_livreur_toggle"),
    path("backoffice/livreurs/new/", views.backoffice_livreur_create, name="backoffice_livreur_create"),

    # Validation commande
    path("commande/valider/", views.valider_commande, name="valider_commande"),
]
