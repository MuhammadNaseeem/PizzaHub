from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect, render

from .models import Cart, CartItem, CartItemAddon
from menu.models import Product, Addon
from customization.models import CustomizationOption, CustomizationRule
from deals.models import Deal

from cart.utils import get_or_create_cart


# ======================================================
# ADD TO CART
# ======================================================
def add_to_cart(request, product_id):

    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method != "POST":
        return redirect('menu:product_detail', slug=product.slug)

    quantity = int(request.POST.get('quantity', 1))

    unit_price = Decimal(product.final_price)

    cart_item = CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity,
        unit_price=unit_price
    )

    # =========================
    # CUSTOMIZATION
    # =========================
    customization_total = Decimal("0.00")
    selected_options = []

    for key, value in request.POST.items():
        if key.startswith("group_"):
            option = CustomizationOption.objects.get(id=value)
            customization_total += option.price

            selected_options.append({
                "group": key,
                "option": option.name,
                "price": float(option.price)
            })

    cart_item.customization_data = selected_options
    cart_item.save()

    # =========================
    # ADDONS
    # =========================
    addon_total = Decimal("0.00")

    for addon_id in request.POST.getlist('addons'):
        addon = get_object_or_404(Addon, id=addon_id)

        CartItemAddon.objects.create(
            cart_item=cart_item,
            addon=addon,
            price=addon.price,
            quantity=1
        )

        addon_total += addon.price

    # =========================
    # FINAL PRICE
    # =========================
    cart_item.unit_price = (
        Decimal(product.final_price)
        + customization_total
        + addon_total
    )

    cart_item.save()

    return redirect('cart:cart_detail')


# ======================================================
# CART DETAIL
# ======================================================
def cart_detail(request):

    cart = get_or_create_cart(request)
    items = CartItem.objects.filter(cart=cart)

    subtotal = Decimal("0.00")
    total_discount = Decimal("0.00")
    deal_discount = Decimal("0.00")

    cart_display_items = []

    for item in items:

        addon_total = sum(a.price * a.quantity for a in item.addons.all())
        line_base_total = (item.unit_price + addon_total) * item.quantity

        selected_options = item.customization_data or []

        best_discount = Decimal("0.00")

        for opt in selected_options:

            option_name = opt.get("option", "").strip()

            rules = CustomizationRule.objects.filter(
                is_active=True,
                trigger_option__name__iexact=option_name
            )

            for rule in rules:

                if rule.discount_type == "fixed":
                    discount = rule.discount_amount * item.quantity
                else:
                    discount = (
                        line_base_total *
                        rule.discount_amount / Decimal("100")
                    )

                best_discount = max(best_discount, discount)

        item_discount = best_discount

        # DEAL DISCOUNT
        if item.deal:
            original_price = item.product.final_price or 0

            deal_discount += (
                original_price
                * item.deal_discount_percent
                / Decimal("100")
                * item.quantity
            )

        final_line_total = line_base_total - item_discount

        subtotal += line_base_total
        total_discount += item_discount

        cart_display_items.append({
            "item": item,
            "addon_total": addon_total,
            "line_total": line_base_total,
            "discount": item_discount,
            "final_total": final_line_total,
        })

    final_total = subtotal - (total_discount + deal_discount)

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "items": cart_display_items,
        "subtotal": subtotal,
        "discount_amount": total_discount,
        "deal_discount": deal_discount,
        "final_total": final_total
    })


# ======================================================
# UPDATE ITEM
# ======================================================
def update_cart_item(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)

    if request.method == "POST":
        qty = int(request.POST.get('quantity', 1))
        if qty > 0:
            item.quantity = qty
            item.save()

    return redirect('cart:cart_detail')


# ======================================================
# REMOVE ITEM
# ======================================================
def remove_from_cart(request, item_id):

    item = get_object_or_404(CartItem, id=item_id)
    item.delete()

    return redirect('cart:cart_detail')


# ======================================================
# ADD DEAL TO CART
# ======================================================
def add_deal_to_cart(request, slug):

    deal = get_object_or_404(
        Deal.objects.prefetch_related('items__product'),
        slug=slug
    )

    cart = get_or_create_cart(request)

    discount_percent = deal.discount_percentage or 0

    for item in deal.items.select_related("product"):

        product = item.product

        base_price = product.final_price or product.sale_price or 0

        discounted_price = base_price - (
            base_price * Decimal(discount_percent) / 100
        )

        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=item.quantity,
            unit_price=discounted_price,
            deal=deal,
            deal_discount_percent=discount_percent
        )

    return redirect("cart:cart_detail")


