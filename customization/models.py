from django.db import models
from menu.models import Product


# ======================================================
# 1. CUSTOMIZATION GROUP (Size, Crust, Toppings, etc.)
# ======================================================
class CustomizationGroup(models.Model):
    SINGLE = "single"
    MULTIPLE = "multiple"

    name = models.CharField(max_length=120)

    selection_type = models.CharField(
        max_length=20,
        choices=[(SINGLE, "Single"), (MULTIPLE, "Multiple")],
        default=SINGLE
    )

    min_select = models.PositiveIntegerField(default=0)
    max_select = models.PositiveIntegerField(default=1)

    display_order = models.PositiveIntegerField(default=0)

    allow_half_selection = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.name


# ======================================================
# 2. CUSTOMIZATION OPTION (Actual selectable item)
# ======================================================
class CustomizationOption(models.Model):
    group = models.ForeignKey(
        CustomizationGroup,
        on_delete=models.CASCADE,
        related_name="options"
    )

    name = models.CharField(max_length=120)

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    is_default = models.BooleanField(default=False)

    is_available = models.BooleanField(default=True)

    image = models.ImageField(upload_to="customization/", null=True, blank=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.group.name} - {self.name}"


# ======================================================
# 3. PRODUCT ↔ CUSTOMIZATION MAPPING
# ======================================================
class ProductCustomizationGroup(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="customization_groups"
    )

    group = models.ForeignKey(CustomizationGroup, on_delete=models.CASCADE)

    is_required = models.BooleanField(default=False)

    min_override = models.PositiveIntegerField(null=True, blank=True)
    max_override = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("product", "group")

    def __str__(self):
        return f"{self.product.name} → {self.group.name}"


# ======================================================
# 4. ADVANCED RULE ENGINE (OPTIONAL BUT POWERFUL)
# ======================================================
# ======================================================
# 4. ADVANCED RULE ENGINE
# ======================================================
class CustomizationRule(models.Model):

    DISCOUNT = "discount"
    FREE_ITEM = "free_item"
    PRICE_OVERRIDE = "price_override"

    RULE_TYPES = [
        (DISCOUNT, "Discount"),
        (FREE_ITEM, "Free Item"),
        (PRICE_OVERRIDE, "Price Override"),
    ]

    FIXED = "fixed"
    PERCENT = "percent"

    DISCOUNT_TYPES = [
        (FIXED, "Fixed Amount"),
        (PERCENT, "Percentage"),
    ]

    name = models.CharField(max_length=200)

    rule_type = models.CharField(
        max_length=30,
        choices=RULE_TYPES
    )

    trigger_group = models.ForeignKey(
        CustomizationGroup,
        on_delete=models.CASCADE,
        related_name="rules"
    )

    trigger_option = models.ForeignKey(
        CustomizationOption,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPES,
        default=FIXED
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    free_option = models.ForeignKey(
        CustomizationOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="free_rules"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    