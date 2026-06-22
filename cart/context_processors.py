from cart.utils import get_or_create_cart

def navbar_context(request):
    cart = get_or_create_cart(request)

    return {
        "cart": cart,
        "cart_items_count": cart.items.count()
    }

