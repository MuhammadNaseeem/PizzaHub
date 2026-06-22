from django import forms
from django.forms import inlineformset_factory
from .models import Deal, DealItem


# =========================
# DEAL FORM
# =========================
class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            'title',
            'slug',
            'description',
            'short_description',
            'banner',
            'thumbnail',
            'deal_type',
            'coupon_code',
            'discount_percentage',
            'discount_amount',
            'buy_quantity',
            'get_quantity',
            'minimum_order_amount',
            'maximum_discount_amount',
            'start_date',
            'end_date',
            'is_active',
            'is_featured',
            'is_flash_sale',
            'show_on_homepage',
            'is_new_customer_only',
            'free_delivery',
            'priority',
            'sort_order',
            'background_color',
            'text_color',
            'badge_text',
            'meta_title',
            'meta_description',
        ]


# =========================
# DEAL ITEM FORMSET
# =========================
DealItemFormSet = inlineformset_factory(
    Deal,
    DealItem,
    fields=('product', 'quantity', 'item_discount'),
    extra=1,
    can_delete=True
)

