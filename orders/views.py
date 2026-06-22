from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from decimal import Decimal   # ✅ ADD THIS

from cart.utils import get_or_create_cart
from orders.models import Order, OrderItem



# =====================================================
# CHECKOUT (FINAL FIXED VERSION)
# =====================================================
@transaction.atomic
def checkout(request):

    cart = get_or_create_cart(request)

    cart_items = cart.items.select_related(
        "product",
        "variant",
        "variant__product"
    )

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    # =========================
    # SAFE TOTAL CALCULATION
    # =========================
    total_price = sum(
        (item.total_price for item in cart_items),
        Decimal("0.00")
    )

    if request.method == "POST":

        payment_method = request.POST.get("payment_method", "cod")

        # =========================
        # CREATE ORDER
        # =========================
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            country=request.POST.get("country"),

            subtotal=total_price,
            total_price=total_price,

            payment_method=payment_method,
            payment_status=(
                "pending"
                if payment_method in ["jazzcash", "easypaisa"]
                else "unpaid"
            ),

            transaction_id=request.POST.get("transaction_id") or None,
            sender_account=request.POST.get("sender_number") or None,
            status="pending",
        )

        # =========================
        # ORDER ITEMS (SAFE + FIXED)
        # =========================
        for item in cart_items:

            # 🔥 SAFE VARIANT RESOLUTION
            variant = item.variant

            if not variant:
                variant = item.product.variants.first()

            if not variant:
                messages.error(
                    request,
                    f"Product '{item.product.name}' has no variant."
                )
                return redirect("cart:cart_detail")

            # =========================
            # CREATE ORDER ITEM
            # =========================
            OrderItem.objects.create(
                order=order,
                variant=variant,
                quantity=item.quantity,
                price=item.unit_price
            )

            # =========================
            # STOCK UPDATE
            # =========================
            if hasattr(variant, "stock") and variant.stock is not None:
                if item.quantity > variant.stock:
                    messages.error(
                        request,
                        f"Not enough stock for {item.product.name}"
                    )
                    return redirect("cart:cart_detail")

                variant.stock -= item.quantity
                variant.save()

        # =========================
        # CLEAR CART
        # =========================
        cart.items.all().delete()

        messages.success(request, "Order placed successfully!")

        return redirect("orders:checkout_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "cart_items": cart_items,
        "total_price": total_price,
    })


# =====================================================
# SUCCESS
# =====================================================
def checkout_success(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    return render(request, "orders/checkout_success.html", {
        "order": order
    })


# =====================================================
# USER ORDERS LIST
# =====================================================
@login_required
def order_list(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(request, "orders/order_list.html", {
        "orders": orders
    })


# =====================================================
# ORDER DETAIL
# =====================================================
@login_required
def order_detail(request, pk):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
            "items__variant",
            "items__variant__product"
        ),
        pk=pk,
        user=request.user
    )

    return render(request, "orders/order_detail.html", {
        "order": order
    })


# =====================================================
# DELETE ORDER
# =====================================================
@login_required
def order_delete(request, pk):

    order = get_object_or_404(
        Order,
        id=pk,
        user=request.user
    )

    if request.method == "POST":

        order.delete()

        messages.success(
            request,
            "Order deleted successfully."
        )

    return redirect("orders:order_list")




