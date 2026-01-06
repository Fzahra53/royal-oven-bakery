from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('produits/', views.produits, name='produits'),
    path('apropos/', views.apropos, name='apropos'),
    path('contact/', views.contact, name='contact'),

    # Auth
    path('connexion/', views.connexion_view, name='connexion'),
    path('inscription/', views.inscription_view, name='inscription'),
    path('mon-compte/', views.mon_compte_view, name='mon_compte'),
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # Panier
    path('mon-panier/', views.mon_panier_view, name='mon_panier'),
    path('panier/ajouter/<int:produit_id>/', views.panier_ajouter, name='panier_ajouter'),
    path('panier/supprimer/<int:produit_id>/', views.panier_supprimer, name='panier_supprimer'),
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

    # Livreur
    path("delivery/orders/", views.delivery_my_orders, name="delivery_my_orders"),
    path("delivery/orders/<int:pk>/update/", views.delivery_update_status, name="delivery_update_status"),
    path("backoffice/livreurs/", views.backoffice_livreurs_list, name="backoffice_livreurs_list"),
    path("backoffice/livreurs/<int:pk>/toggle/", views.backoffice_livreur_toggle, name="backoffice_livreur_toggle"),



    path("commande/valider/", views.valider_commande, name="valider_commande"),
    path("backoffice/livreurs/new/", views.backoffice_livreur_create, name="backoffice_livreur_create"),


]
