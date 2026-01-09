from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from datetime import timedelta

from .models import Commande, Livreur, Livraison, LigneCommande, Produit, Client, Categorie, Avis
from .forms import ProduitForm

# ==================== VUES PUBLIQUES ====================

def accueil(request):
    """Page d'accueil - Affiche les catégories"""
    categories = Categorie.objects.all()
    produits = Produit.objects.filter(actif=True)[:6]  # Montrer 6 produits actifs
    return render(request, "bakeryapp/accueil.html", {
        "categories": categories,
        "produits": produits
    })

def produits(request):
    """Page liste des produits"""
    produits_list = Produit.objects.filter(actif=True)
    categories = Categorie.objects.all()
    return render(request, "bakeryapp/produits.html", {
        "produits": produits_list,
        "categories": categories
    })

def apropos(request):
    """Page À propos"""
    return render(request, "bakeryapp/apropos.html")

def contact(request):
    """Page Contact"""
    return render(request, "bakeryapp/contact.html")

# ==================== AUTHENTIFICATION ====================

def connexion_view(request):
    """Connexion utilisateur"""
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
    
    return render(request, "bakeryapp/connexion.html")

def inscription_view(request):
    """Inscription utilisateur"""
    if request.method == "POST":
        prenom = request.POST.get("prenom", "").strip()
        nom = request.POST.get("nom", "").strip()
        telephone = request.POST.get("telephone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        adresse = request.POST.get("adresse", "").strip()
        ville = request.POST.get("ville", "Rabat").strip()

        # Validations
        if not email or not password or not nom:
            messages.error(request, "Veuillez remplir les champs obligatoires.")
            return redirect("inscription")

        # Éviter doublons
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("inscription")

        if Client.objects.filter(email__iexact=email).exists():
            messages.error(request, "Ce client existe déjà.")
            return redirect("inscription")

        # Créer user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom,
        )

        # Créer profil client
        Client.objects.create(
            user=user,
            nom=f"{prenom} {nom}".strip(),
            telephone=telephone,
            email=email,
            adresse=adresse,
            ville=ville or "Rabat",
        )

        messages.success(request, "Compte créé ✅")
        return redirect("connexion")

    return render(request, "bakeryapp/inscription.html")

def deconnexion_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')

# ==================== COMPTE UTILISATEUR ====================

@login_required
def mon_compte_view(request):
    """Page mon compte"""
    client = getattr(request.user, "profil_client", None)
    
    # Nom à afficher
    nom_a_afficher = ""
    if client:
        nom_a_afficher = client.nom
    elif request.user.get_full_name():
        nom_a_afficher = request.user.get_full_name()
    else:
        nom_a_afficher = request.user.username
    
    # Compter les commandes
    commandes_count = 0
    livraisons_count = 0
    
    if client:
        commandes_count = Commande.objects.filter(client=client).count()
        
        # Livraisons cette semaine
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

@login_required
def mes_commandes_view(request):
    """Historique des commandes"""
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
    """Détail d'une commande"""
    commande = get_object_or_404(Commande, pk=pk, client__user=request.user)
    lignes = commande.lignes.select_related('produit').all()
    
    context = {
        'commande': commande,
        'lignes': lignes,
    }
    return render(request, 'bakeryapp/detail_commande.html', context)

@login_required
def modifier_profil_view(request):
    """Modifier le profil"""
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

# ==================== PANIER ====================

def _get_panier(request):
    """Récupérer le panier de la session"""
    return request.session.get("panier", {})

def _save_panier(request, panier):
    """Sauvegarder le panier dans la session"""
    request.session["panier"] = panier
    request.session.modified = True

@login_required
def mon_panier_view(request):
    """Voir le panier"""
    # DEBUG: Afficher le contenu de la session
    print("Session panier:", request.session.get('panier', {}))
    print("Session key:", request.session.session_key)
    
    panier = request.session.get('panier', {})
    
    if not panier:
        print("Panier vide dans la session")
        return render(request, "bakeryapp/mon_panier.html", {
            "items": [],
            "total": 0,
            "panier_count": 0
        })
    
    # Convertir les clés en int pour la requête
    produit_ids = []
    for key in panier.keys():
        try:
            produit_ids.append(int(key))
        except ValueError:
            continue
    
    print("IDs produits dans panier:", produit_ids)
    
    # Récupérer les produits
    produits = Produit.objects.filter(id__in=produit_ids)
    print("Produits trouvés:", list(produits.values_list('id', 'nom')))
    
    items = []
    total = 0.0

    for p in produits:
        qty = panier.get(str(p.id), 0)
        if qty > 0:
            subtotal = float(p.prix_actuel()) * qty
            total += subtotal

            items.append({
                "produit": p,
                "qty": qty,
                "subtotal": subtotal
            })
    
    print("Items calculés:", items)
    print("Total calculé:", total)
    
    context = {
        "items": items,
        "total": total,
        "panier_count": len(panier)
    }
    
    return render(request, "bakeryapp/mon_panier.html", context)

@login_required
def panier_ajouter(request, produit_id):
    """Ajouter un produit au panier"""
    produit = get_object_or_404(Produit, id=produit_id)

    if produit.stock <= 0:
        messages.error(request, "Produit en rupture de stock.")
        return redirect("produits")

    # Récupérer ou initialiser le panier
    panier = request.session.get('panier', {})
    
    # Convertir produit_id en string (clé de session)
    produit_key = str(produit_id)
    
    # Ajouter ou incrémenter la quantité
    if produit_key in panier:
        panier[produit_key] += 1
    else:
        panier[produit_key] = 1
    
    # Sauvegarder dans la session
    request.session['panier'] = panier
    
    # Forcer la sauvegarde de la session
    request.session.modified = True
    
    messages.success(request, f"✅ {produit.nom} ajouté au panier.")
    
    # Rediriger vers la page précédente ou le panier
    referer = request.META.get('HTTP_REFERER', 'mon_panier')
    return redirect(referer)

@login_required
def panier_supprimer(request, produit_id):
    """Supprimer un produit du panier"""
    panier = _get_panier(request)
    key = str(produit_id)

    if key in panier:
        del panier[key]
        _save_panier(request, panier)
        messages.success(request, "Produit supprimé du panier.")

    return redirect("mon_panier")

@login_required
def panier_modifier_quantite(request, produit_id):
    """Modifier la quantité dans le panier"""
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

@login_required
def valider_commande(request):
    """Valider une commande"""
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

    # Vider le panier
    request.session["panier"] = {}

    messages.success(request, f"Commande #{commande.id} créée ✅")
    return redirect("mon_compte")




@login_required
def debug_panier(request):
    """Page de debug pour voir le contenu de la session"""
    panier = request.session.get('panier', {})
    
    debug_info = {
        'session_key': request.session.session_key,
        'panier_content': panier,
        'user': request.user.username,
        'produits_in_panier': [],
    }
    
    if panier:
        produit_ids = [int(pid) for pid in panier.keys()]
        produits = Produit.objects.filter(id__in=produit_ids)
        debug_info['produits_in_panier'] = [
            {'id': p.id, 'nom': p.nom, 'qty': panier[str(p.id)]}
            for p in produits
        ]
    
    return JsonResponse(debug_info)









# AJOUTEZ CETTE FONCTION POUR VIDER LE PANIER
@login_required
def panier_vider(request):
    """Vider complètement le panier"""
    if request.method == "POST":
        request.session["panier"] = {}
        messages.success(request, "Panier vidé avec succès.")
    else:
        # Si appelé en GET, demander confirmation
        return render(request, "bakeryapp/panier_vider_confirm.html")
    
    return redirect("mon_panier")

# ==================== PRODUITS & RECHERCHE ====================

def produits_par_categorie(request, categorie_id):
    """Produits par catégorie"""
    categorie = get_object_or_404(Categorie, id=categorie_id)
    produits = Produit.objects.filter(categorie=categorie, actif=True)
    
    context = {
        'categorie': categorie,
        'produits': produits,
        'categories': Categorie.objects.all(),
    }
    return render(request, 'bakeryapp/produits_categorie.html', context)

def produit_detail(request, produit_id):
    """Détail d'un produit"""
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

@login_required
def ajouter_avis(request, produit_id):
    """Ajouter un avis"""
    produit = get_object_or_404(Produit, id=produit_id)
    client = getattr(request.user, "profil_client", None)
    
    if not client:
        messages.error(request, "Vous devez avoir un profil client pour laisser un avis")
        return redirect('produit_detail', produit_id=produit_id)
    
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
        
        avis, created = Avis.objects.update_or_create(
            client=client,
            produit=produit,
            defaults={
                'note': note,
                'commentaire': commentaire,
                'approuve': False
            }
        )
        
        messages.success(request, "Votre avis a été soumis.")
        return redirect('produit_detail', produit_id=produit_id)
    
    return redirect('produit_detail', produit_id=produit_id)

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

# ==================== FAVORIS ====================

@login_required
def ajouter_favori(request, produit_id):
    """Ajouter aux favoris"""
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
    """Retirer des favoris"""
    favoris = request.session.get('favoris', [])
    
    if produit_id in favoris:
        favoris.remove(produit_id)
        request.session['favoris'] = favoris
        messages.success(request, "Produit retiré des favoris")
    
    return redirect('mes_favoris')

@login_required
def mes_favoris(request):
    """Voir les favoris"""
    favoris_ids = request.session.get('favoris', [])
    produits = Produit.objects.filter(id__in=favoris_ids, actif=True)
    
    context = {
        'produits': produits,
    }
    return render(request, 'bakeryapp/mes_favoris.html', context)

# ==================== BACKOFFICE ====================

@login_required
def backoffice_dashboard(request):
    """Tableau de bord backoffice"""
    return render(request, "backoffice/dashboard.html")

@login_required
def backoffice_products_list(request):
    """Liste des produits backoffice"""
    produits = Produit.objects.all().order_by("-id")
    return render(request, "backoffice/products_list.html", {"produits": produits})

@login_required
def backoffice_product_create(request):
    """Créer un produit"""
    if request.method == "POST":
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Produit créé ✅")
            return redirect("backoffice_products_list")
    else:
        form = ProduitForm()

    return render(request, "backoffice/product_form.html", {"form": form})

@login_required
def backoffice_product_update(request, pk):
    """Modifier un produit"""
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
    """Supprimer un produit"""
    produit = get_object_or_404(Produit, pk=pk)

    if request.method == "POST":
        produit.delete()
        messages.success(request, "Produit supprimé ✅")
        return redirect("backoffice_products_list")

    return render(request, "backoffice/product_confirm_delete.html", {"produit": produit})

@login_required
def backoffice_orders_list(request):
    """Liste des commandes"""
    commandes = Commande.objects.all().order_by("-date_commande")
    return render(request, "backoffice/orders_list.html", {"commandes": commandes})

@login_required
def backoffice_order_detail(request, pk):
    """Détail d'une commande"""
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
    """Liste des livreurs"""
    livreurs = Livreur.objects.all().order_by("-id")
    return render(request, "backoffice/livreurs_list.html", {"livreurs": livreurs})

@login_required
def backoffice_livreur_toggle(request, pk):
    """Activer/désactiver livreur"""
    livreur = get_object_or_404(Livreur, pk=pk)
    livreur.disponible = not livreur.disponible
    livreur.save(update_fields=["disponible"])
    messages.success(request, "Disponibilité mise à jour ✅")
    return redirect("backoffice_livreurs_list")

@login_required
def backoffice_assign_livreur(request, pk):
    """Assigner un livreur"""
    commande = get_object_or_404(Commande, pk=pk)
    livreurs = Livreur.objects.filter(disponible=True).order_by("nom")

    if request.method == "POST":
        livreur_id = request.POST.get("livreur_id")
        livreur = get_object_or_404(Livreur, pk=livreur_id)

        livraison, created = Livraison.objects.get_or_create(commande=commande)
        livraison.livreur = livreur
        livreur.disponible = False
        livreur.save(update_fields=["disponible"])

        livraison.statut = "EN_LIVRAISON"
        livraison.date_livraison = timezone.now()
        livraison.save()

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
def backoffice_livreur_create(request):
    """Créer un livreur"""
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

# ==================== LIVREUR ====================

@login_required
def delivery_my_orders(request):
    """Commandes du livreur"""
    livreur = Livreur.objects.filter(nom=request.user.username).first()

    if not livreur:
        messages.error(request, "Aucun profil livreur associé à ce compte.")
        return redirect("accueil")

    livraisons = Livraison.objects.filter(livreur=livreur).order_by("-id")
    return render(request, "delivery/my_orders.html", {"livraisons": livraisons, "livreur": livreur})

@login_required
def delivery_update_status(request, pk):
    """Mettre à jour statut livraison"""
    livraison = get_object_or_404(Livraison, pk=pk)

    if request.method == "POST":
        new_status = request.POST.get("statut")
        livraison.statut = new_status
        livraison.save(update_fields=["statut"])

        if new_status == "LIVREE" and livraison.livreur:
            livreur = livraison.livreur
            livreur.disponible = True
            livreur.save(update_fields=["disponible"])

        messages.success(request, "Statut de livraison mis à jour ✅")
        return redirect("delivery_my_orders")

    return render(request, "delivery/update_status.html", {"livraison": livraison})

from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Categorie

def is_admin(user):
    """Vérifie si l'utilisateur est admin"""
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def gestion_categories(request):
    """Interface pour gérer les catégories"""
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "ajouter":
            nom = request.POST.get("nom", "").strip()
            description = request.POST.get("description", "").strip()
            
            if nom:
                categorie, created = Categorie.objects.get_or_create(
                    nom=nom,
                    defaults={"description": description}
                )
                if created:
                    messages.success(request, f"Catégorie '{nom}' ajoutée")
                else:
                    messages.warning(request, f"Catégorie '{nom}' existe déjà")
                    
        elif action == "supprimer":
            categorie_id = request.POST.get("categorie_id")
            try:
                categorie = Categorie.objects.get(id=categorie_id)
                nom = categorie.nom
                categorie.delete()
                messages.success(request, f"Catégorie '{nom}' supprimée")
            except Categorie.DoesNotExist:
                messages.error(request, "Catégorie non trouvée")
    
    categories = Categorie.objects.all().order_by('nom')
    return render(request, 'backoffice/gestion_categories.html', {'categories': categories})

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from django.utils import timezone

@login_required
def generer_facture_pdf(request, commande_id):
    """Génère une facture PDF pour une commande"""
    commande = get_object_or_404(Commande, id=commande_id, client__user=request.user)
    
    # Créer la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture-commande-{commande.id}.pdf"'
    
    # Créer le PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # En-tête
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, "ROYAL OVEN BAKERY")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, "Agdal, Rabat • Maroc")
    p.drawString(50, height - 85, "Tél: +212 6 12 34 56 78")
    p.drawString(50, height - 100, "Email: contact@royaloven.com")
    
    # Titre
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 130, f"FACTURE N° {commande.id}")
    
    # Informations client
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 160, "CLIENT:")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 175, f"{commande.client.nom}")
    p.drawString(50, height - 190, f"{commande.client.adresse}")
    p.drawString(50, height - 205, f"{commande.client.ville}")
    p.drawString(50, height - 220, f"Email: {commande.client.email}")
    
    # Informations commande
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, height - 160, "COMMANDE:")
    p.setFont("Helvetica", 10)
    p.drawString(300, height - 175, f"N°: {commande.id}")
    p.drawString(300, height - 190, f"Date: {commande.date_commande.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(300, height - 205, f"Statut: {commande.get_statut_display()}")
    
    # Ligne séparatrice
    p.line(50, height - 240, width - 50, height - 240)
    
    # Détails commande
    y_position = height - 260
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y_position, "PRODUIT")
    p.drawString(250, y_position, "QUANTITÉ")
    p.drawString(320, y_position, "PRIX UNIT.")
    p.drawString(400, y_position, "TOTAL")
    
    y_position -= 20
    p.setFont("Helvetica", 9)
    
    total = 0
    for ligne in commande.lignes.all():
        p.drawString(50, y_position, ligne.produit.nom)
        p.drawString(250, y_position, f"{ligne.quantite}")
        p.drawString(320, y_position, f"{ligne.prix_unitaire:.2f} DH")
        sous_total = ligne.quantite * ligne.prix_unitaire
        p.drawString(400, y_position, f"{sous_total:.2f} DH")
        total += sous_total
        y_position -= 15
    
    # Ligne séparatrice
    p.line(50, y_position - 10, width - 50, y_position - 10)
    
    # Total
    y_position -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(320, y_position, "TOTAL:")
    p.drawString(400, y_position, f"{total:.2f} DH")
    
    # Mentions
    y_position -= 50
    p.setFont("Helvetica", 8)
    p.drawString(50, y_position, "Merci pour votre commande !")
    p.drawString(50, y_position - 15, "Livraison offerte dans Rabat pour les commandes de plus de 100 DH")
    
    # Pied de page
    p.setFont("Helvetica", 8)
    p.drawString(50, 30, f"Généré le {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    p.drawString(width - 150, 30, "Page 1/1")
    
    # Finaliser le PDF
    p.showPage()
    p.save()
    
    return response


from django.contrib.auth.decorators import login_required
from .models import Categorie

def gestion_categories_simple(request):
    """Affiche les 4 catégories principales"""
    categories = Categorie.objects.filter(
        nom__in=["Viennoiseries", "Pains", "Pâtisseries", "Spécialités Maison"]
    ).order_by('nom')
    
    # Si manquantes, les créer
    if categories.count() < 4:
        categories_defaut = [
            ("Viennoiseries", "Croissants, pains au chocolat, chaussons"),
            ("Pains", "Pains traditionnels, baguettes, pains spéciaux"),
            ("Pâtisseries", "Gâteaux, tartes, éclairs, desserts"),
            ("Spécialités Maison", "Produits spéciaux et saisonniers"),
        ]
        
        for nom, description in categories_defaut:
            Categorie.objects.get_or_create(
                nom=nom,
                defaults={'description': description}
            )
        
        categories = Categorie.objects.filter(
            nom__in=["Viennoiseries", "Pains", "Pâtisseries", "Spécialités Maison"]
        )
    
    return render(request, 'bakeryapp/categories.html', {
        'categories': categories,
        'total_produits': sum(c.produit_set.count() for c in categories)
    })