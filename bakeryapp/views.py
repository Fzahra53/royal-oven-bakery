

from django.shortcuts import render
from .models import Commande, Livreur, Livraison, LigneCommande
from .models import Produit
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Client
from .models import Categorie
from .forms import ProduitForm
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models 

def accueil(request):
    produits = Produit.objects.all()[:6]
    return render(request, "bakeryapp/accueil.html", {"produits": produits})

def produits(request):
    produits_list = Produit.objects.filter(actif=True)
    categories = Categorie.objects.all()
    return render(request, "bakeryapp/produits.html", {
        "produits": produits_list,
        "categories": categories
    })

def apropos(request):
    return render(request, "bakeryapp/apropos.html")


def contact(request):
    return render(request, "bakeryapp/contact.html")

from .models import Categorie

def accueil(request):
    categories = Categorie.objects.all()
    return render(request, "bakeryapp/accueil.html", {"categories": categories})



from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# ---------------- BACKOFFICE (stubs to make URLs work) ----------------

@login_required
def backoffice_dashboard(request):
    return render(request, "backoffice/dashboard.html")




@login_required
def backoffice_products_list(request):
    produits = Produit.objects.all().order_by("-id")
    return render(
        request,
        "backoffice/products_list.html",
        {"produits": produits}
    )



@login_required
def backoffice_product_create(request):
    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("backoffice_products_list")
    else:
        form = ProduitForm()

    return render(request, "backoffice/product_form.html", {"form": form})


@login_required
def backoffice_product_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES, instance=produit)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié ✅")
            return redirect("backoffice_products_list")
    else:
        form = ProduitForm(instance=produit)

    return render(request, "backoffice/product_form.html", {"form": form, "produit": produit})



@login_required
@require_http_methods(["GET", "POST"])
def backoffice_product_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé ✅")
        return redirect("backoffice_products_list")

    return render(request, "backoffice/product_confirm_delete.html", {"produit": produit})




@login_required
def backoffice_orders_list(request):
    commandes = Commande.objects.all().order_by("-date_commande")
    return render(request, "backoffice/orders_list.html", {"commandes": commandes})


@login_required
def backoffice_order_detail(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    livraison = Livraison.objects.filter(commande=commande).first()
    lignes = commande.lignes.select_related("produit").all()

    return render(
        request,
        "backoffice/order_detail.html",
        {"commande": commande, "livraison": livraison, "lignes": lignes},
    )

@login_required
def backoffice_livreurs_list(request):
    livreurs = Livreur.objects.all().order_by("-id")
    return render(request, "backoffice/livreurs_list.html", {"livreurs": livreurs})


@login_required
def backoffice_livreur_toggle(request, pk):
    livreur = get_object_or_404(Livreur, pk=pk)
    livreur.disponible = not livreur.disponible
    livreur.save(update_fields=["disponible"])
    messages.success(request, "Disponibilité mise à jour ✅")
    return redirect("backoffice_livreurs_list")






@login_required
def backoffice_assign_livreur(request, pk):
    commande = get_object_or_404(Commande, pk=pk)
    livreurs = Livreur.objects.filter(disponible=True).order_by("nom")

    if request.method == "POST":
        livreur_id = request.POST.get("livreur_id")  # name=livreur_id dans le form
        livreur = get_object_or_404(Livreur, pk=livreur_id)

        # Crée ou récupère la livraison liée à la commande
        livraison, created = Livraison.objects.get_or_create(commande=commande)

        livraison.livreur = livreur
        livreur.disponible = False
        livreur.save(update_fields=["disponible"])

        livraison.statut = "EN_LIVRAISON"
        livraison.date_livraison = timezone.now()
        livraison.save()

        # Optionnel: mettre aussi le statut commande
        commande.statut = "EN_LIVRAISON"
        commande.save(update_fields=["statut"])

        messages.success(request, f"Livreur affecté : {livreur.nom} ✅")
        return redirect("backoffice_order_detail", pk=commande.id)

    return render(
        request,
        "backoffice/assign_livreur.html",
        {"commande": commande, "livreurs": livreurs},
    )


@login_required
def delivery_my_orders(request):
    livreur = Livreur.objects.filter(nom=request.user.username).first()

    # si tu n'as pas encore de login livreur lié, on évite le crash
    if not livreur:
        messages.error(request, "Aucun profil livreur associé à ce compte.")
        return redirect("accueil")

    livraisons = Livraison.objects.filter(livreur=livreur).order_by("-id")
    return render(request, "delivery/my_orders.html", {"livraisons": livraisons, "livreur": livreur})


@login_required
def delivery_update_status(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("statut")

        livraison.statut = new_status
        livraison.save(update_fields=["statut"])

        # 👉 SI la livraison est terminée, le livreur redevient disponible
        if new_status == "LIVREE" and livraison.livreur:
            livreur = livraison.livreur
            livreur.disponible = True
            livreur.save(update_fields=["disponible"])

        messages.success(request, "Statut de livraison mis à jour ✅")
        return redirect("delivery_my_orders")

    return render(
        request,
        "delivery/update_status.html",
        {"livraison": livraison},
    )




@login_required
def valider_commande(request):
    # récupérer ou créer le profil client
    client, _ = Client.objects.get_or_create(
        user=request.user,
        defaults={
            "nom": (request.user.get_full_name() or request.user.username),
            "telephone": "",
            "email": request.user.email or f"{request.user.username}@local.test",
            "adresse": "",
            "ville": "Rabat",
        },
    )

    panier = request.session.get("panier", {})

    if not panier:
        messages.error(request, "Panier vide.")
        return redirect("produits")

    commande = Commande.objects.create(
        client=client,
        statut="EN_ATTENTE",
        adresse_livraison=client.adresse,
    )

    total = 0

    for produit_id, qty in panier.items():
        produit = get_object_or_404(Produit, id=produit_id)
        prix = produit.prix_actuel()

        LigneCommande.objects.create(
            commande=commande,
            produit=produit,
            quantite=qty,
            prix_unitaire=prix,
        )

        total += prix * qty
        produit.stock -= qty
        produit.save()

    commande.montant_total = total
    commande.save()

    # vider le panier
    request.session["panier"] = {}

    messages.success(request, f"Commande #{commande.id} créée ✅")
    return redirect("mon_compte")


@login_required
def backoffice_livreur_create(request):
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        vehicule = request.POST.get("vehicule", "").strip()

        if not nom or not telephone:
            messages.error(request, "Nom et téléphone obligatoires.")
            return redirect("backoffice_livreur_create")

        Livreur.objects.create(
            nom=nom,
            telephone=telephone,
            vehicule=vehicule,
            disponible=True,
        )

        messages.success(request, "Livreur créé ✅")
        return redirect("backoffice_orders_list")

    return render(request, "backoffice/livreur_form.html")


# Vue pour la connexion




def connexion_view(request):
    if request.method == "POST":
        identifiant = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        
        User = get_user_model()
        user = None
        
        # Essayer d'abord avec l'identifiant comme username
        user = authenticate(request, username=identifiant, password=password)
        
        # Si échec et que c'est un email
        if user is None and "@" in identifiant:
            try:
                # Chercher le premier utilisateur avec cet email
                user_with_email = User.objects.filter(email__iexact=identifiant).first()
                if user_with_email:
                    user = authenticate(
                        request, 
                        username=user_with_email.username, 
                        password=password
                    )
            except Exception as e:
                print(f"Erreur lors de la recherche par email: {e}")
        
        if user is not None:
            login(request, user)
            messages.success(request, "Connexion réussie !")
            return redirect("mon_compte")
        else:
            messages.error(request, "Identifiant ou mot de passe incorrect.")
            return redirect("connexion")
    
    # GET request - afficher le formulaire
    return render(request, "bakeryapp/connexion.html")




def inscription_view(request):
    if request.method == "POST":
        prenom = request.POST.get("prenom", "").strip()
        nom = request.POST.get("nom", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        adresse = request.POST.get("adresse", "").strip()
        ville = request.POST.get("ville", "Rabat").strip()

        # validations rapides
        if not email or not password or not nom:
            messages.error(request, "Veuillez remplir les champs obligatoires.")
            return redirect("inscription")

        # éviter doublons
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("inscription")

        if Client.objects.filter(email__iexact=email).exists():
            messages.error(request, "Ce client existe déjà.")
            return redirect("inscription")

        # créer user (Django auth)
        user = User.objects.create_user(
            username=email,          # on garde email comme username
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom,
        )

        # créer profil client lié
        Client.objects.create(
            user=user,
            nom=f"{prenom} {nom}".strip(),
            telephone=telephone,
            email=email,
            adresse=adresse,
            ville=ville or "Rabat",
        )

        messages.success(request, "Compte créé ✅ يمكنك الآن تسجيل الدخول.")
        return redirect("connexion")

    return render(request, "bakeryapp/inscription.html")


# Vue pour la page compte (protégée)


@login_required
def mon_compte_view(request):
    client = getattr(request.user, "profil_client", None)
    
    # Si client n'existe pas, créer ou utiliser user
    nom_a_afficher = ""
    if client:
        nom_a_afficher = client.nom
    elif request.user.get_full_name():
        nom_a_afficher = request.user.get_full_name()
    else:
        nom_a_afficher = request.user.username
    
    # Compter les commandes
    commandes_count = 0
    if client:
        commandes_count = Commande.objects.filter(client=client).count()
    
    # Calculer les livraisons de cette semaine (exemple)
    livraisons_count = 0
    if client:
        from datetime import timedelta
        from django.utils import timezone
        semaine_passee = timezone.now() - timedelta(days=7)
        livraisons_count = Commande.objects.filter(
            client=client,
            date_commande__gte=semaine_passee,
            statut="LIVREE"
        ).count()
    
    context = {
        "client": client,
        "nom_affichage": nom_a_afficher,
        "panier_count": len(request.session.get("panier", {})),
        "commandes_count": commandes_count,
        "livraisons_count": livraisons_count,
    }
    return render(request, "bakeryapp/mon_compte.html", context)


# Vue pour la déconnexion
def deconnexion_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')


# -------------------------


# -------------------------
# PANIER (version simple avec session)
# -------------------------

def _get_panier(request):
    # format: {"produit_id": quantite}
    return request.session.get("panier", {})

def _save_panier(request, panier):
    request.session["panier"] = panier
    request.session.modified = True


@login_required
def mon_panier_view(request):
    panier = _get_panier(request)

    ids = [int(pid) for pid in panier.keys()] if panier else []
    produits = Produit.objects.filter(id__in=ids)

    items = []
    total = 0.0

    for p in produits:
        qty = int(panier.get(str(p.id), 0))
        # ✅ ton modèle a prix_actuel()
        subtotal = float(p.prix_actuel()) * qty
        total += subtotal

        items.append({
            "produit": p,
            "qty": qty,
            "subtotal": subtotal
        })

    return render(request, "bakeryapp/mon_panier.html", {"items": items, "total": total})


@login_required
def panier_ajouter(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)

    # ✅ option: bloquer si rupture de stock
    if produit.stock <= 0:
        messages.error(request, "Produit en rupture de stock.")
        return redirect("produits")

    panier = _get_panier(request)
    key = str(produit.id)
    panier[key] = int(panier.get(key, 0)) + 1
    _save_panier(request, panier)

    # ✅ ton modèle a nom
    messages.success(request, f"{produit.nom} ajouté au panier.")
    return redirect("mon_panier")


@login_required
def panier_supprimer(request, produit_id):
    panier = _get_panier(request)
    key = str(produit_id)

    if key in panier:
        del panier[key]
        _save_panier(request, panier)
        messages.success(request, "Produit supprimé du panier.")

    return redirect("mon_panier")

# -------------------------
# VUES POUR LE COMPTE CLIENT
# -------------------------

@login_required
def mes_commandes_view(request):
    """Afficher l'historique des commandes du client"""
    client = getattr(request.user, "profil_client", None)
    commandes = []
    
    if client:
        commandes = Commande.objects.filter(client=client).order_by('-date_commande')[:10]
    
    context = {
        'client': client,
        'commandes': commandes,
        'commandes_count': commandes.count() if client else 0,
    }
    return render(request, 'bakeryapp/mes_commandes.html', context)

@login_required
def detail_commande_view(request, pk):
    """Détail d'une commande spécifique"""
    commande = get_object_or_404(Commande, pk=pk, client__user=request.user)
    lignes = commande.lignes.select_related('produit').all()
    
    context = {
        'commande': commande,
        'lignes': lignes,
    }
    return render(request, 'bakeryapp/detail_commande.html', context)

@login_required
def modifier_profil_view(request):
    client = getattr(request.user, "profil_client", None)
    
    if request.method == "POST":
        nom = request.POST.get("nom", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        adresse = request.POST.get("adresse", "").strip()
        ville = request.POST.get("ville", "Rabat").strip()
        
        if client:
            client.nom = nom
            client.telephone = telephone
            client.adresse = adresse
            client.ville = ville
            client.save()
            messages.success(request, "Profil mis à jour !")
        else:
            # Créer le client
            client = Client.objects.create(
                user=request.user,
                nom=nom,
                telephone=telephone,
                email=request.user.email,
                adresse=adresse,
                ville=ville
            )
            messages.success(request, "Profil créé !")
        
        return redirect("mon_compte")
    
    return render(request, "bakeryapp/modifier_profil.html", {"client": client})

# -------------------------
# FONCTIONNALITÉS PANIER AMÉLIORÉES
# -------------------------

@login_required
def panier_modifier_quantite(request, produit_id):
    """Modifier la quantité d'un produit dans le panier"""
    if request.method == "POST":
        action = request.POST.get("action")
        panier = _get_panier(request)
        key = str(produit_id)
        
        if key in panier:
            if action == "augmenter":
                produit = get_object_or_404(Produit, id=produit_id)
                if produit.stock > panier[key]:
                    panier[key] += 1
                    messages.success(request, f"Quantité augmentée pour {produit.nom}")
                else:
                    messages.error(request, "Stock insuffisant")
            elif action == "diminuer":
                if panier[key] > 1:
                    panier[key] -= 1
                    messages.success(request, "Quantité diminuée")
                else:
                    del panier[key]
                    messages.success(request, "Produit supprimé du panier")
            elif action == "supprimer":
                del panier[key]
                messages.success(request, "Produit supprimé du panier")
        
        _save_panier(request, panier)
    
    return redirect("mon_panier")

# -------------------------
# FONCTIONNALITÉS PRODUITS
# -------------------------

def produits_par_categorie(request, categorie_id):
    """Afficher les produits par catégorie"""
    categorie = get_object_or_404(Categorie, id=categorie_id)
    produits = Produit.objects.filter(categorie=categorie, actif=True)
    
    context = {
        'categorie': categorie,
        'produits': produits,
        'categories': Categorie.objects.all(),
    }
    return render(request, 'bakeryapp/produits_categorie.html', context)

def produit_detail(request, produit_id):
    """Détail d'un produit avec avis"""
    produit = get_object_or_404(Produit, id=produit_id, actif=True)
    avis = produit.avis.filter(approuve=True)[:5]
    
    context = {
        'produit': produit,
        'avis': avis,
        'produits_similaires': Produit.objects.filter(
            categorie=produit.categorie, 
            actif=True
        ).exclude(id=produit.id)[:4],
    }
    return render(request, 'bakeryapp/produit_detail.html', context)

# -------------------------
# FONCTIONNALITÉS AVIS
# -------------------------

@login_required
def ajouter_avis(request, produit_id):
    """Ajouter un avis sur un produit"""
    produit = get_object_or_404(Produit, id=produit_id)
    client = getattr(request.user, "profil_client", None)
    
    if not client:
        messages.error(request, "Vous devez avoir un profil client pour laisser un avis")
        return redirect('produit_detail', produit_id=produit_id)
    
    # Vérifier si le client a déjà commandé ce produit
    a_commande = Commande.objects.filter(
        client=client,
        lignes__produit=produit,
        statut="LIVREE"
    ).exists()
    
    if not a_commande:
        messages.error(request, "Vous devez avoir commandé ce produit pour laisser un avis")
        return redirect('produit_detail', produit_id=produit_id)
    
    if request.method == "POST":
        note = request.POST.get("note", 5)
        commentaire = request.POST.get("commentaire", "").strip()
        
        # Créer ou mettre à jour l'avis
        avis, created = Avis.objects.update_or_create(
            client=client,
            produit=produit,
            defaults={
                'note': note,
                'commentaire': commentaire,
                'approuve': False  # Nécessite validation admin
            }
        )
        
        messages.success(request, "Votre avis a été soumis. Il sera publié après modération.")
        return redirect('produit_detail', produit_id=produit_id)
    
    return redirect('produit_detail', produit_id=produit_id)

# -------------------------
# FONCTIONNALITÉS FAVORIS
# -------------------------

@login_required
def ajouter_favori(request, produit_id):
    """Ajouter un produit aux favoris"""
    produit = get_object_or_404(Produit, id=produit_id)
    favoris = request.session.get('favoris', [])
    
    if produit_id not in favoris:
        favoris.append(produit_id)
        request.session['favoris'] = favoris
        messages.success(request, f"{produit.nom} ajouté aux favoris ❤️")
    else:
        messages.info(request, f"{produit.nom} est déjà dans vos favoris")
    
    return redirect(request.META.get('HTTP_REFERER', 'produits'))

@login_required
def retirer_favori(request, produit_id):
    """Retirer un produit des favoris"""
    favoris = request.session.get('favoris', [])
    
    if produit_id in favoris:
        favoris.remove(produit_id)
        request.session['favoris'] = favoris
        messages.success(request, "Produit retiré des favoris")
    
    return redirect('mes_favoris')

@login_required
def mes_favoris(request):
    """Afficher la liste des produits favoris"""
    favoris_ids = request.session.get('favoris', [])
    produits = Produit.objects.filter(id__in=favoris_ids, actif=True)
    
    context = {
        'produits': produits,
    }
    return render(request, 'bakeryapp/mes_favoris.html', context)

# -------------------------
# FONCTIONNALITÉS RECHERCHE
# -------------------------

def recherche(request):
    """Recherche de produits"""
    query = request.GET.get('q', '').strip()
    produits = []
    
    if query:
        produits = Produit.objects.filter(
            models.Q(nom__icontains=query) | 
            models.Q(description__icontains=query),
            actif=True
        )[:20]
    
    context = {
        'query': query,
        'produits': produits,
        'nombre_resultats': produits.count(),
    }
    return render(request, 'bakeryapp/recherche.html', context)

