import uuid
from django.db import models
from django.conf import settings
from menu.models import Product, ProductVariant, Addon


class Cart(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id}"
    


from decimal import Decimal
from django.db import models


class CartItem(models.Model):

    cart = models.ForeignKey(
        'Cart',
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        'menu.Product',
        on_delete=models.CASCADE
    )

    variant = models.ForeignKey(
        'menu.ProductVariant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # =========================
    # 🔥 DEAL SUPPORT (FIX)
    # =========================
    deal = models.ForeignKey(
        'deals.Deal',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cart_items"
    )

    deal_discount_percent = models.PositiveIntegerField(default=0)

    # =========================
    # CUSTOMIZATION STORAGE
    # =========================
    customization_data = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # ADDONS
    # =========================
    @property
    def addon_total(self):
        return sum(
            (a.price * a.quantity)
            for a in self.addons.all()
        )

    # =========================
    # CUSTOMIZATION TOTAL
    # =========================
    @property
    def customization_total(self):

        if not self.customization_data:
            return Decimal('0.00')

        total = Decimal('0.00')

        for item in self.customization_data:
            total += Decimal(str(item.get("price", 0)))

        return total

    # =========================
    # FINAL TOTAL (FIXED)
    # =========================
    @property
    def total_price(self):

        base = self.unit_price
        addons = self.addon_total
        custom = self.customization_total

        return (base + addons + custom) * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    



class CartItemAddon(models.Model):

    cart_item = models.ForeignKey(
        'CartItem',
        on_delete=models.CASCADE,
        related_name="addons"
    )

    addon = models.ForeignKey(
        'menu.Addon',
        on_delete=models.CASCADE
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # CLEAN CALCULATION
    # =========================
    @property
    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.addon.name} x {self.quantity}"
