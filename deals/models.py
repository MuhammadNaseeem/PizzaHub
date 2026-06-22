from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from decimal import Decimal

from menu.models import Product, Category


# =====================================================
# DEAL MODEL (PRODUCTION READY)
# =====================================================
class Deal(models.Model):

    class DealType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Percentage Discount'
        FIXED = 'fixed', 'Fixed Amount Discount'
        BOGO = 'bogo', 'Buy One Get One'
        COMBO = 'combo', 'Combo Deal'
        FREE_DELIVERY = 'free_delivery', 'Free Delivery'

    # ---------------- BASIC ----------------
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=255, blank=True)

    banner = models.ImageField(upload_to='deals/')
    thumbnail = models.ImageField(upload_to='deals/thumbnails/', blank=True, null=True)

    deal_type = models.CharField(max_length=20, choices=DealType.choices)

    # ---------------- DISCOUNT ----------------
    coupon_code = models.CharField(max_length=50, blank=True, db_index=True)

    discount_percentage = models.PositiveIntegerField(blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    buy_quantity = models.PositiveIntegerField(default=1)
    get_quantity = models.PositiveIntegerField(default=0)

    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # ---------------- RELATIONS ----------------
    products = models.ManyToManyField(Product, blank=True, related_name='deals')
    categories = models.ManyToManyField(Category, blank=True, related_name='deals')

    # ---------------- USAGE CONTROL ----------------
    usage_limit = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    max_uses_per_user = models.PositiveIntegerField(default=1)

    # ---------------- TIMING ----------------
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # ---------------- STATUS ----------------
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=True)
    is_new_customer_only = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)

    # ---------------- UI ----------------
    priority = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveIntegerField(default=0)

    background_color = models.CharField(max_length=20, blank=True)
    text_color = models.CharField(max_length=20, blank=True)
    badge_text = models.CharField(max_length=50, blank=True)

    # ---------------- ANALYTICS ----------------
    views = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)

    # ---------------- SEO ----------------
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)

    # ---------------- SYSTEM ----------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', '-is_featured', 'sort_order']
        indexes = [
            models.Index(fields=['coupon_code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['deal_type']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    # =====================================================
    # CLEAN VALIDATION
    # =====================================================
    def clean(self):
        super().clean()

        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError("End date must be greater than start date.")

        if self.deal_type == self.DealType.PERCENTAGE:
            if self.discount_percentage is None:
                raise ValidationError("Percentage deal requires discount_percentage.")
            if not (0 < self.discount_percentage <= 100):
                raise ValidationError("Discount must be between 1 and 100.")

        if self.deal_type == self.DealType.FIXED:
            if self.discount_amount is None:
                raise ValidationError("Fixed deal requires discount_amount.")
            if self.discount_amount < 0:
                raise ValidationError("Discount cannot be negative.")

        if self.deal_type in [self.DealType.BOGO, self.DealType.COMBO]:
            if not self.pk and not self.products.exists():
                # allow save first, but will validate in admin/form save
                pass

    # =====================================================
    # SAVE (SAFE SLUG)
    # =====================================================
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug

            while Deal.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{get_random_string(4)}"

            self.slug = slug

        super().save(*args, **kwargs)

    # =====================================================
    # STATUS
    # =====================================================
    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def status(self):
        now = timezone.now()

        if self.start_date and self.start_date > now:
            return "upcoming"
        if self.end_date and self.end_date < now:
            return "expired"
        if not self.is_active:
            return "inactive"
        return "active"

    # =====================================================
    # PRICING ENGINE (CLEAN + SAFE)
    # =====================================================
    @property
    def original_price(self):
        if not self.pk:
            return Decimal("0.00")

        total = Decimal("0.00")

        items = self.items.select_related("product")

        for item in items:
            product = item.product

            price = (
                getattr(product, "final_price", None)
                or getattr(product, "sale_price", None)
                or getattr(product, "price", 0)
            )

            total += Decimal(str(price)) * Decimal(item.quantity)

        return total

    @property
    def discounted_price(self):
        original = self.original_price

        if original <= 0:
            return Decimal("0.00")

        discount = Decimal("0.00")

        # Percentage discount
        if self.deal_type == self.DealType.PERCENTAGE and self.discount_percentage:
            discount = (original * Decimal(self.discount_percentage)) / Decimal("100")

        # Fixed discount
        elif self.deal_type == self.DealType.FIXED and self.discount_amount:
            discount = Decimal(self.discount_amount)

        # Apply max discount cap
        if self.maximum_discount_amount:
            discount = min(discount, Decimal(self.maximum_discount_amount))

        final_price = original - discount
        return max(final_price, Decimal("0.00"))

    @property
    def savings(self):
        return max(Decimal("0.00"), self.original_price - self.discounted_price)

    @property
    def savings_percentage(self):
        if self.original_price <= 0:
            return 0
        return int((self.savings / self.original_price) * 100)


# =====================================================
# DEAL ITEM MODEL
# =====================================================
class DealItem(models.Model):

    deal = models.ForeignKey(
        Deal,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    item_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    class Meta:
        unique_together = ('deal', 'product')
        ordering = ['id']

    def __str__(self):
        return f"{self.deal.title} - {self.product.name}"

    @property
    def total_price(self):
        price = getattr(self.product, "sale_price", None) or self.product.price
        return Decimal(str(price)) * Decimal(self.quantity)
    

    