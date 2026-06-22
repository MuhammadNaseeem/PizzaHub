from .models import Cart

def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
    else:
        if not request.session.session_key:
            request.session.save()

        session_id = request.session.session_key

        cart, _ = Cart.objects.get_or_create(
            session_id=session_id,
            is_active=True
        )

    return cart


from decimal import Decimal
from customization.models import CustomizationRule


def calculate_discount(subtotal, selected_options):

    total_discount = Decimal("0.00")

    for opt in selected_options:

        rules = CustomizationRule.objects.filter(
            is_active=True,
            trigger_option__name=opt.get("option")
        )

        for rule in rules:

            if rule.discount_type == "fixed":
                total_discount += rule.discount_amount

            elif rule.discount_type == "percent":
                total_discount += (
                    subtotal * rule.discount_amount / Decimal("100")
                )

    return total_discount


from .models import Cart

def get_or_create_cart(request):

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            is_active=True
        )
        return cart

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_id=session_id,
        is_active=True
    )

    return cart
