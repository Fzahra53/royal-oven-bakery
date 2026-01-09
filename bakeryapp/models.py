from django.db import models
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils import timezone
from django.conf import settings



class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom


class Produit(models.Model):
    TYPE_CHOICES = [
        ("PAIN", "Pain"),
        ("VIENNOISERIE", "Viennoiserie"),
        ("PATISSERIE", "Pâtisserie"),
        ("SANDWICH", "Sandwich"),
        ("BOISSON", "Boisson"),
        ("AUTRE", "Autre"),
    ]

    nom = models.CharField(max_length=150)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name="produits")
    type_produit = models.CharField(max_length=20, choices=TYPE_CHOICES, default="AUTRE")

    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    stock = models.PositiveIntegerField(default=0)

    # Choisis UNE approche image :
    # 1) upload (recommandé si tu gères MEDIA)
    image = models.ImageField(upload_to="produits/", blank=True, null=True)
    # 2) ou URL externe (si tu préfères des images hébergées ailleurs)
    image_url = models.URLField(blank=True, null=True)

    est_populaire = models.BooleanField(default=False)
    actif = models.BooleanField(default=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_maj = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        constraints = [
            # évite deux produits avec le même nom en ignorant maj/min (Postgres OK, SQLite parfois limité)
            UniqueConstraint(Lower("nom"), name="uniq_produit_nom_ci"),
        ]

    def __str__(self):
        return f"{self.nom} - {self.prix_actuel()}"

    def prix_actuel(self):
        return self.prix_promo if self.prix_promo is not None else self.prix


class Client(models.Model):
    # Remplace "mot_de_passe" par le système Django (meilleur)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="profil_client")

    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)

    adresse = models.TextField()
    ville = models.CharField(max_length=100, default="Rabat")

    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nom"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.nom


class Livreur(models.Model):
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    vehicule = models.CharField(max_length=50, blank=True)
    disponible = models.BooleanField(default=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="livreur_profile",
    )

    class Meta:
        verbose_name = "Livreur"
        verbose_name_plural = "Livreurs"

    def __str__(self):
        return self.nom


class Commande(models.Model):
    STATUT_CHOICES = [
        ("PANIER", "Panier"),
        ("EN_ATTENTE", "En attente"),
        ("VALIDEE", "Validée"),
        ("EN_PREPARATION", "En préparation"),
        ("EN_LIVRAISON", "En livraison"),
        ("LIVREE", "Livrée"),
        ("ANNULEE", "Annulée"),
    ]

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="commandes")
    date_commande = models.DateTimeField(auto_now_add=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="PANIER")

    montant_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    adresse_livraison = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date_commande"]
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"

    def __str__(self):
        return f"Commande #{self.id} - {self.client.nom}"

    def recalculer_total(self, save=True):
        total = sum((ligne.sous_total() for ligne in self.lignes.all()), start=0)
        self.montant_total = total
        if save:
            self.save(update_fields=["montant_total"])
        return total


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name="lignes")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name="lignes_commande")

    quantite = models.PositiveIntegerField(default=1)
    # prix figé au moment de la commande (important si le prix change après)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        constraints = [
            UniqueConstraint(fields=["commande", "produit"], name="uniq_commande_produit")
        ]

    def __str__(self):
        return f"{self.quantite}x {self.produit.nom}"

    def sous_total(self):
        return self.quantite * self.prix_unitaire


class Livraison(models.Model):
    STATUT_CHOICES = [
        ("EN_PREPARATION", "En préparation"),
        ("EN_LIVRAISON", "En livraison"),
        ("LIVREE", "Livrée"),
        ("ANNULEE", "Annulée"),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="livraison")
    livreur = models.ForeignKey(Livreur, on_delete=models.SET_NULL, null=True, blank=True, related_name="livraisons")

    date_livraison = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="EN_PREPARATION")

    adresse_livraison = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Livraison"
        verbose_name_plural = "Livraisons"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # ✅ Synchroniser le statut de la commande avec le statut de la livraison
        # (adapte uniquement si tes valeurs de Commande.statut sont différentes)
        if hasattr(self.commande, "statut"):
            self.commande.statut = self.statut
            self.commande.save(update_fields=["statut"])

    def __str__(self):
        return f"Livraison #{self.id} - Cmd {self.commande_id}"



class Facture(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name="facture")
    date_facture = models.DateTimeField(default=timezone.now)

    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    numero = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def __str__(self):
        return f"Facture {self.numero} - Cmd {self.commande_id}"


class Avis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="avis")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name="avis")

    note = models.PositiveSmallIntegerField(default=5)
    commentaire = models.TextField(blank=True)

    date_publication = models.DateTimeField(auto_now_add=True)
    approuve = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Avis"
        verbose_name_plural = "Avis"
        constraints = [
            UniqueConstraint(fields=["client", "produit"], name="uniq_avis_client_produit")
        ]

    def __str__(self):
        return f"Avis de {self.client} sur {self.produit}"
