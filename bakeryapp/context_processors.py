from django.conf import settings

def cart_context(request):
    """Ajoute le contexte du panier à tous les templates"""
    cart = request.session.get('panier', {})
    cart_count = sum(cart.values()) if cart else 0
    
    favorites = request.session.get('favoris', [])
    favorites_count = len(favorites) if favorites else 0
    
    return {
        'cart_count': cart_count,
        'cart_items': cart,
        'favorites_count': favorites_count,
        'delivery_fee': getattr(settings, 'DELIVERY_FEE', 20.00),
        'free_delivery_threshold': getattr(settings, 'FREE_DELIVERY_THRESHOLD', 100.00),
        'bakery_name': getattr(settings, 'BAKERY_NAME', 'Royal Oven'),
        'bakery_phone': getattr(settings, 'BAKERY_PHONE', '+212 6 12 34 56 78'),
        'bakery_email': getattr(settings, 'BAKERY_EMAIL', 'contact_royal_oven@gmail.com'),
        'delivery_time': getattr(settings, 'DELIVERY_TIME', '30-45 minutes'),
    }


def global_context(request):
    """Contexte global pour tous les templates"""
    from bakeryapp.models import Categorie
    
    categories = Categorie.objects.all()
    
    return {
        'categories': categories,
        'debug': settings.DEBUG,
        'current_path': request.path,
    }