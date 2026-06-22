from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Deal, DealItem


# =====================================================
# DEAL ITEM INLINE
# =====================================================
class DealItemInline(admin.TabularInline):
    model = DealItem
    extra = 1
    autocomplete_fields = ['product']


# =====================================================
# DEAL ADMIN
# =====================================================
@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):

    inlines = [DealItemInline]

    list_display = (
        'title',
        'deal_type',
        'coupon_code',
        'discount_preview',
        'savings_preview',
        'status_badge',
        'is_featured',
        'is_active',
        'views',
        'clicks',
    )

    list_filter = (
        'deal_type',
        'is_active',
        'is_featured',
        'is_flash_sale',
        'show_on_homepage',
        'is_new_customer_only',
        'free_delivery',
        'start_date',
        'end_date',
    )

    search_fields = (
        'title',
        'coupon_code',
        'short_description',
    )

    ordering = ('-priority', '-created_at')

    list_editable = ('is_active', 'is_featured')

    prepopulated_fields = {'slug': ('title',)}

    autocomplete_fields = ('products', 'categories')

    readonly_fields = (
        'views',
        'clicks',
        'used_count',
        'remaining_uses_display',
        'status_preview',
        'savings_preview',
        'created_at',
        'updated_at',
    )

    save_on_top = True
    date_hierarchy = 'created_at'

    # =====================================================
    # DISPLAY METHODS
    # =====================================================

    def discount_preview(self, obj):
        if obj.deal_type == Deal.DealType.PERCENTAGE and obj.discount_percentage:
            return f"{obj.discount_percentage}% OFF"

        if obj.deal_type == Deal.DealType.FIXED and obj.discount_amount:
            return f"Rs {obj.discount_amount} OFF"

        if obj.deal_type == Deal.DealType.BOGO:
            return f"Buy {obj.buy_quantity} Get {obj.get_quantity}"

        if obj.free_delivery:
            return "🚚 FREE DELIVERY"

        return "-"

    discount_preview.short_description = "Discount"

    def savings_preview(self, obj):
        if not obj:
            return "-"
        return f"Rs {obj.savings}"

    savings_preview.short_description = "Savings"

    def status_badge(self, obj):
        if not obj or not obj.start_date or not obj.end_date:
            return "⚪ Draft"

        now = timezone.now()

        if obj.end_date < now:
            return "🔴 Expired"

        if obj.start_date > now:
            return "🟡 Upcoming"

        if not obj.is_active:
            return "⚫ Inactive"

        return "🟢 Active"

    status_badge.short_description = "Status"

    def status_preview(self, obj):
        return self.status_badge(obj)

    status_preview.short_description = "Current Status"

    def remaining_uses_display(self, obj):
        if not obj:
            return "-"

        if obj.usage_limit == 0:
            return "Unlimited"

        return max(0, obj.usage_limit - obj.used_count)

    remaining_uses_display.short_description = "Remaining Uses"


# =====================================================
# DEAL ITEM ADMIN
# =====================================================
@admin.register(DealItem)
class DealItemAdmin(admin.ModelAdmin):

    list_display = (
        'deal',
        'product',
        'quantity',
        'item_discount',
    )

    list_filter = ('deal',)

    search_fields = (
        'deal__title',
        'product__name',
    )

    autocomplete_fields = ('deal', 'product')

    list_select_related = ('deal', 'product')

    