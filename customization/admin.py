from django.contrib import admin
from .models import (
    CustomizationGroup,
    CustomizationOption,
    ProductCustomizationGroup,
    CustomizationRule
)


# ======================================================
# 1. OPTIONS INLINE (Inside Group)
# ======================================================
class CustomizationOptionInline(admin.TabularInline):
    model = CustomizationOption
    extra = 1
    fields = ("name", "price", "is_default", "is_available", "image")
    show_change_link = True


# ======================================================
# 2. CUSTOMIZATION GROUP ADMIN
# ======================================================
@admin.register(CustomizationGroup)
class CustomizationGroupAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "selection_type",
        "min_select",
        "max_select",
        "display_order",
        "is_active",
    )

    list_filter = ("selection_type", "is_active")
    search_fields = ("name",)
    ordering = ("display_order",)

    inlines = [CustomizationOptionInline]


# ======================================================
# 3. CUSTOMIZATION OPTION ADMIN
# ======================================================
@admin.register(CustomizationOption)
class CustomizationOptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "group",
        "price",
        "is_default",
        "is_available",
    )

    list_filter = ("group", "is_default", "is_available")
    search_fields = ("name",)
    list_editable = ("price", "is_default", "is_available")


# ======================================================
# 4. PRODUCT ↔ CUSTOMIZATION LINK ADMIN
# ======================================================
@admin.register(ProductCustomizationGroup)
class ProductCustomizationGroupAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "group",
        "is_required",
        "min_override",
        "max_override",
    )

    list_filter = ("is_required", "group")
    search_fields = ("product__name", "group__name")
    autocomplete_fields = ("product", "group")


# ======================================================
# 5. RULE ENGINE ADMIN (ADVANCED)
# ======================================================
@admin.register(CustomizationRule)
class CustomizationRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "rule_type",
        "trigger_group",
        "trigger_option",
        "is_active",
    )

    list_filter = ("rule_type", "is_active", "trigger_group")
    search_fields = ("name",)

    autocomplete_fields = (
        "trigger_group",
        "trigger_option",
        "free_option",
    )

    