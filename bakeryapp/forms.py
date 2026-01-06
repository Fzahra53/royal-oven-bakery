from django import forms
from .models import Produit, Livreur, Livraison


class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            "nom",
            "categorie",
            "type_produit",
            "description",
            "prix",
            "prix_promo",
            "stock",
            "image",
            "image_url",
            "est_populaire",
            "actif",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class AssignLivreurForm(forms.Form):
    livreur = forms.ModelChoiceField(
        queryset=Livreur.objects.filter(disponible=True),
        empty_label="-- Choisir un livreur --",
        required=True,
    )


class UpdateLivraisonStatutForm(forms.ModelForm):
    class Meta:
        model = Livraison
        fields = ["statut", "date_livraison", "adresse_livraison", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "adresse_livraison": forms.Textarea(attrs={"rows": 2}),
        }
