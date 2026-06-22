from decimal import Decimal
from customization.models import CustomizationRule


def get_product_discount(product):

    # get product option IDs (IMPORTANT FIX)
    product_option_ids = set(
        product.customization_groups.values_list("group__options__id", flat=True)
    )

    rules = CustomizationRule.objects.filter(
        is_active=True,
        rule_type="discount",
        discount_type="percent"
    )

    max_discount = Decimal("0.00")

    for rule in rules:

        # ✅ FIX: match OPTION not GROUP
        if rule.trigger_option_id in product_option_ids:

            if rule.discount_amount > max_discount:
                max_discount = rule.discount_amount

    return float(max_discount) if max_discount > 0 else 0

