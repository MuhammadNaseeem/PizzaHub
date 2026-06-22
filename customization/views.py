from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from menu.models import Product

from .models import (
    CustomizationGroup,
    CustomizationOption,
    ProductCustomizationGroup,
    CustomizationRule
)


# ======================================================
# 1. PRODUCT CUSTOMIZATION STRUCTURE (API)
# ======================================================
@require_http_methods(["GET"])
def product_customization(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    product_groups = ProductCustomizationGroup.objects.filter(
        product=product
    ).select_related("group")

    data = []

    for pg in product_groups:
        group = pg.group

        options = CustomizationOption.objects.filter(
            group=group,
            is_available=True
        )

        data.append({
            "group_id": group.id,
            "group_name": group.name,
            "selection_type": group.selection_type,
            "is_required": pg.is_required,

            "min_select": pg.min_override if pg.min_override is not None else group.min_select,
            "max_select": pg.max_override if pg.max_override is not None else group.max_select,

            "allow_half_selection": group.allow_half_selection,

            "options": [
                {
                    "id": opt.id,
                    "name": opt.name,
                    "price": float(opt.price),
                    "image": opt.image.url if opt.image else None,
                    "is_default": opt.is_default,
                }
                for opt in options
            ]
        })

    return JsonResponse({
        "product_id": product.id,
        "product_name": product.name,
        "customization": data
    })


# ======================================================
# 2. VALIDATION ENGINE (CORE LOGIC)
# ======================================================
@require_http_methods(["POST"])
def validate_customization(request):
    """
    Expected JSON:
    {
        "product_id": 1,
        "selections": [
            {
                "group_id": 2,
                "options": [1, 2]
            }
        ]
    }
    """

    try:
        body = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    product_id = body.get("product_id")
    selections = body.get("selections", [])

    product = get_object_or_404(Product, id=product_id)

    errors = []

    for sel in selections:
        group_id = sel.get("group_id")
        option_ids = sel.get("options", [])

        pg = get_object_or_404(
            ProductCustomizationGroup,
            product=product,
            group_id=group_id
        )

        group = pg.group

        min_req = pg.min_override if pg.min_override is not None else group.min_select
        max_req = pg.max_override if pg.max_override is not None else group.max_select

        # -----------------------------
        # Basic validation
        # -----------------------------
        if len(option_ids) < min_req:
            errors.append(f"{group.name}: minimum {min_req} required")

        if len(option_ids) > max_req:
            errors.append(f"{group.name}: maximum {max_req} allowed")

        # -----------------------------
        # Validate option belongs to group
        # -----------------------------
        valid_ids = set(
            CustomizationOption.objects.filter(
                group=group
            ).values_list("id", flat=True)
        )

        for oid in option_ids:
            if oid not in valid_ids:
                errors.append(f"{group.name}: invalid option selected")

        # -----------------------------
        # SINGLE selection enforcement
        # -----------------------------
        if group.selection_type == CustomizationGroup.SINGLE and len(option_ids) > 1:
            errors.append(f"{group.name}: only one option allowed")

    if errors:
        return JsonResponse({
            "valid": False,
            "errors": errors
        }, status=400)

    return JsonResponse({
        "valid": True,
        "message": "Customization is valid"
    })


# ======================================================
# 3. GROUP DETAIL API (UI SUPPORT)
# ======================================================
@require_http_methods(["GET"])
def customization_group_detail(request, group_id):
    group = get_object_or_404(CustomizationGroup, id=group_id)

    options = CustomizationOption.objects.filter(
        group=group,
        is_available=True
    )

    return JsonResponse({
        "group_id": group.id,
        "group_name": group.name,
        "selection_type": group.selection_type,
        "allow_half_selection": group.allow_half_selection,

        "options": [
            {
                "id": opt.id,
                "name": opt.name,
                "price": float(opt.price),
                "image": opt.image.url if opt.image else None,
                "is_default": opt.is_default,
            }
            for opt in options
        ]
    })


# ======================================================
# 4. RULE ENGINE HOOK (FUTURE-READY)
# ======================================================
def apply_rules(selected_option_ids):
    """
    Placeholder for advanced pricing logic
    (discounts, free items, overrides)
    """

    rules = CustomizationRule.objects.filter(is_active=True)

    applied = []

    for rule in rules:
        if rule.trigger_option_id in selected_option_ids:
            applied.append({
                "rule": rule.name,
                "type": rule.rule_type,
                "discount": float(rule.discount_amount)
            })

    return applied


# ======================================================
# 5. PRODUCT CUSTOMIZATION PAGE (TEMPLATE)
# ======================================================
from django.shortcuts import get_object_or_404, render
from menu.models import Product
from customization.models import (
    ProductCustomizationGroup,
    CustomizationOption,
    CustomizationRule
)


def product_customization_page(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    # =========================
    # PRODUCT CUSTOMIZATION GROUPS
    # =========================
    product_groups = (
        ProductCustomizationGroup.objects
        .filter(product=product)
        .select_related("group")
        .order_by("id")
    )

    customization = []

    for pg in product_groups:

        group = pg.group

        options = (
            CustomizationOption.objects
            .filter(group=group, is_available=True)
            .order_by("id")
        )

        customization.append({
            "group_id": group.id,
            "group_name": group.name,
            "selection_type": group.selection_type,
            "is_required": pg.is_required,

            "min_select": (
                pg.min_override
                if pg.min_override is not None
                else group.min_select
            ),

            "max_select": (
                pg.max_override
                if pg.max_override is not None
                else group.max_select
            ),

            "allow_half_selection": group.allow_half_selection,

            "options": list(options)
        })

    # =========================
    # DISCOUNT RULE (20% OFF)
    # =========================
    discount_rule = (
        CustomizationRule.objects
        .filter(
            is_active=True,
            discount_type="percent",
            trigger_group__productcustomizationgroup__product=product
        )
        .distinct()
        .first()
    )

    discount_percent = (
        discount_rule.discount_amount
        if discount_rule
        else None
    )

    # =========================
    # RENDER TEMPLATE
    # =========================
    return render(request, "customization/product_customizer.html", {
        "product": product,
        "customization": customization,
        "has_customization": len(customization) > 0,
        "discount_percent": discount_percent,
    })



# ======================================================
# 6. HEALTH CHECK
# ======================================================
@require_http_methods(["GET"])
def customization_health(request):
    return JsonResponse({
        "status": "ok",
        "message": "Customization system working properly"
    })



