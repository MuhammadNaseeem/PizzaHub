from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()

# =====================================================
# CATEGORY
# =====================================================

class Category(models.Model):
    name = models.CharField(max_length=100)

    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True
    )

    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True
    )

    description = models.TextField(
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['sort_order']
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =====================================================
# TAGS
# =====================================================

class Tag(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


# =====================================================
# PRODUCT
# =====================================================

class Product(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='products'
    )

    name = models.CharField(
        max_length=255
    )

    slug = models.SlugField(
        unique=True,
        blank=True,
        db_index=True
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    short_description = models.CharField(
        max_length=255,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    thumbnail = models.ImageField(
        upload_to='products/thumbnails/'
    )

    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    stock_quantity = models.PositiveIntegerField(
        default=0
    )

    preparation_time = models.PositiveIntegerField(
        default=15,
        help_text="Preparation time in minutes"
    )

    calories = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    is_available = models.BooleanField(
        default=True,
        db_index=True
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True
    )

    views = models.PositiveIntegerField(
        default=0
    )

    total_orders = models.PositiveIntegerField(
        default=0
    )

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    meta_title = models.CharField(
        max_length=255,
        blank=True
    )

    meta_description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.name)

        if not self.sku:
            self.sku = str(uuid.uuid4())[:8].upper()

        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.sale_price or self.base_price

    def __str__(self):
        return self.name


# =====================================================
# PRODUCT IMAGES
# =====================================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='products/gallery/'
    )

    is_primary = models.BooleanField(
        default=False
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    class Meta:
        ordering = ['sort_order']

    def save(self, *args, **kwargs):

        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(
                id=self.id
            ).update(
                is_primary=False
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} Image"


# =====================================================
# PRODUCT REVIEW
# =====================================================

class ProductReview(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product}"


# =====================================================
# ADDONS
# =====================================================

class Addon(models.Model):

    name = models.CharField(
        max_length=100
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return self.name


# =====================================================
# PRODUCT VARIANTS
# =====================================================

class ProductVariant(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    name = models.CharField(
        max_length=100
    )

    sku = models.CharField(
        max_length=50,
        unique=True
    )

    image = models.ImageField(
        upload_to='variants/',
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.product.name} - {self.name}"


# =====================================================
# PROMOTIONS
# =====================================================

class Promotion(models.Model):

    title = models.CharField(
        max_length=255
    )

    image = models.ImageField(
        upload_to='offers/'
    )

    discount_percentage = models.PositiveIntegerField()

    start_date = models.DateTimeField()

    end_date = models.DateTimeField()

    is_active = models.BooleanField(
        default=True
    )

    def clean(self):

        if self.end_date <= self.start_date:
            raise ValidationError(
                "End date must be greater than start date."
            )

    def __str__(self):
        return self.title
    
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
    