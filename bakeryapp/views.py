

from django.shortcuts import render
from .models import Produit
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Client
from .models import Categorie



def accueil(request):
    produits = Produit.objects.all()[:6]
    return render(request, "bakeryapp/accueil.html", {"produits": produits})


def produits(request):
    produits = Produit.objects.all()
    return render(request, "bakeryapp/produits.html", {"produits": produits})


def apropos(request):
    return render(request, "bakeryapp/apropos.html")


def contact(request):
    return render(request, "bakeryapp/contact.html")

from .models import Categorie

def accueil(request):
    categories = Categorie.objects.all()
    return render(request, "bakeryapp/accueil.html", {"categories": categories})





    
      
    





# Vue pour la connexion


def connexion_view(request):
    if request.method == "POST":
        email = request.POST.get("email","").strip().lower()
        password = request.POST.get("password","")

        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect("connexion")

        login(request, user)
        return redirect("mon_compte")

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

    context = {
        "client": client,
        "panier_count": 0,        # pour l’instant
        "commandes_count": 0,
        "livraisons_count": 0,
        "commandes": [],
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

