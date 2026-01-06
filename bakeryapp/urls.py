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
