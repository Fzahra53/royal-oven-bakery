from django.contrib import admin
from .models import *


class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix', 'stock', 'est_populaire')
    list_filter = ('categorie', 'type_produit', 'est_populaire')
    search_fields = ('nom', 'description')
    list_editable = ('prix', 'stock', 'est_populaire')


class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'ville', 'date_inscription')
    search_fields = ('nom', 'email', 'telephone')
    list_filter = ('ville',)


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1


class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date_commande', 'statut', 'montant_total')
    list_filter = ('statut', 'date_commande')
    search_fields = ('client__nom', 'id')
    inlines = [LigneCommandeInline]
    readonly_fields = ('montant_total',)


class LivraisonAdmin(admin.ModelAdmin):
    list_display = ('id', 'commande', 'livreur', 'statut', 'date_livraison')
    list_filter = ('statut', 'livreur')
    list_editable = ('statut',)


# Enregistrement des modèles
admin.site.register(Categorie)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Commande, CommandeAdmin)
admin.site.register(LigneCommande)
admin.site.register(Livreur)
admin.site.register(Livraison, LivraisonAdmin)
admin.site.register(Facture)
admin.site.register(Avis)


