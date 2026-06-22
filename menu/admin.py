from django.contrib import admin
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import (
    Category,
    Product,
    ProductImage,
    Tag,
    ProductReview,
    Addon,
    ProductVariant,
    Promotion,
)


# =====================================================
# IMAGE PREVIEW MIXIN
# =====================================================

class ImagePreviewMixin:

    def image_preview(self, obj):

        image = None

        if hasattr(obj, 'image') and obj.image:
            image = obj.image.url

        elif hasattr(obj, 'thumbnail') and obj.thumbnail:
            image = obj.thumbnail.url

        if image:
            return format_html(
                '<img src="{}" width="70" height="70" style="border-radius:8px;object-fit:cover;" />',
                image
            )

        return "No Image"

    image_preview.short_description = "Preview"


# =====================================================
# INLINES
# =====================================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


# =====================================================
# CATEGORY
# =====================================================

@admin.register(Category)
class CategoryAdmin(ImagePreviewMixin, ImportExportModelAdmin):

    list_display = (
        'image_preview',
        'name',
        'is_active',
        'sort_order',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'is_active',
    )

    list_editable = (
        'sort_order',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }


# =====================================================
# TAG
# =====================================================

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    search_fields = ('name',)
    list_display = ('name',)


# =====================================================
# PRODUCT
# =====================================================

@admin.register(Product)
class ProductAdmin(ImagePreviewMixin, ImportExportModelAdmin):

    inlines = [
        ProductImageInline,
        ProductVariantInline,
    ]

    list_display = (
        'image_preview',
        'name',
        'category',
        'base_price',
        'sale_price',
        'stock_quantity',
        'is_featured',
        'is_available',
    )

    list_filter = (
        'category',
        'is_featured',
        'is_available',
    )

    search_fields = (
        'name',
        'sku',
    )

    list_editable = (
        'is_featured',
        'is_available',
        'stock_quantity',
    )

    filter_horizontal = (
        'tags',
    )

    readonly_fields = (
        'views',
        'total_orders',
        'average_rating',
        'created_at',
        'updated_at',
        'image_preview',
    )

    prepopulated_fields = {
        'slug': ('name',)
    }

    actions = [
        'make_featured',
        'make_available',
        'make_unavailable',
    ]

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    make_featured.short_description = "Mark selected products as featured"

    def make_available(self, request, queryset):
        queryset.update(is_available=True)

    make_available.short_description = "Mark selected products available"

    def make_unavailable(self, request, queryset):
        queryset.update(is_available=False)

    make_unavailable.short_description = "Mark selected products unavailable"


# =====================================================
# PRODUCT IMAGE
# =====================================================

@admin.register(ProductImage)
class ProductImageAdmin(ImagePreviewMixin, admin.ModelAdmin):

    list_display = (
        'image_preview',
        'product',
        'is_primary',
        'sort_order',
    )

    list_filter = (
        'is_primary',
    )


# =====================================================
# PRODUCT REVIEW
# =====================================================

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'user',
        'rating',
        'created_at',
    )

    list_filter = (
        'rating',
    )

    search_fields = (
        'product__name',
        'user__username',
    )


# =====================================================
# ADDON
# =====================================================

@admin.register(Addon)
class AddonAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'price',
        'is_active',
    )

    list_editable = (
        'price',
        'is_active',
    )


# =====================================================
# VARIANT
# =====================================================

@admin.register(ProductVariant)
class ProductVariantAdmin(ImagePreviewMixin, admin.ModelAdmin):

    list_display = (
        'image_preview',
        'product',
        'name',
        'price',
        'stock',
        'is_active',
    )

    list_editable = (
        'price',
        'stock',
        'is_active',
    )


# =====================================================
# PROMOTION
# =====================================================

@admin.register(Promotion)
class PromotionAdmin(ImagePreviewMixin, admin.ModelAdmin):

    list_display = (
        'image_preview',
        'title',
        'discount_percentage',
        'start_date',
        'end_date',
        'is_active',
    )

    list_editable = (
        'is_active',
    )