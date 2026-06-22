from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Prefetch
from django.utils import timezone

from .models import Deal

from django.shortcuts import get_object_or_404, redirect
from .models import Deal
from cart.models import CartItem
from cart.utils import get_or_create_cart


# =====================================================
# 🔥 BASE QUERY (OPTIMIZED)
# =====================================================
def get_active_deals():
    now = timezone.now()

    return Deal.objects.prefetch_related(
        Prefetch('items')
    ).filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )


# =====================================================
# 📌 DEAL LIST PAGE
# =====================================================
from django.shortcuts import render
from django.db.models import Q
from .utils import get_active_deals


def deal_list(request):

    deals = get_active_deals().prefetch_related("items__product")

    deal_type = request.GET.get('type')
    featured = request.GET.get('featured')
    flash = request.GET.get('flash')
    search = request.GET.get('search')
    category = request.GET.get('category')

    if deal_type:
        deals = deals.filter(deal_type=deal_type)

    if featured == 'true':
        deals = deals.filter(is_featured=True)

    if flash == 'true':
        deals = deals.filter(is_flash_sale=True)

    if category:
        deals = deals.filter(categories__id=category)

    if search:
        deals = deals.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search) |
            Q(description__icontains=search) |
            Q(coupon_code__icontains=search)
        )

    deals = deals.distinct()

    # ✅ FORCE EVALUATION OF CALCULATED FIELDS (IMPORTANT FIX)
    for deal in deals:
        _ = deal.original_price
        _ = deal.discounted_price
        _ = deal.savings
        _ = deal.savings_percentage

    return render(request, "deals/deal_list.html", {
        "deals": deals
    })



# =====================================================
# 📌 DETAIL PAGE
# =====================================================
from django.shortcuts import get_object_or_404, render
from django.db.models import F

from .models import Deal


# =====================================================
# 📌 DETAIL PAGE (IMPROVED)
# =====================================================
def deal_detail(request, slug):

    deal = get_object_or_404(
        Deal.objects.prefetch_related('items__product'),
        slug=slug
    )

    # ✅ SAFE + ATOMIC VIEW INCREMENT
    Deal.objects.filter(pk=deal.pk).update(
        views=F('views') + 1
    )

    # refresh only required fields (not full reload heavy)
    deal.refresh_from_db(fields=["views"])

    return render(request, "deals/deal_detail.html", {
        "deal": deal
    })


# =====================================================
# ⭐ FEATURED DEALS
# =====================================================
def featured_deals(request):
    deals = get_active_deals().filter(is_featured=True).prefetch_related("items__product")

    return render(request, "deals/featured.html", {"deals": deals})


def flash_deals(request):
    deals = get_active_deals().filter(is_flash_sale=True).prefetch_related("items__product")

    return render(request, "deals/flash.html", {"deals": deals})


def home_deals(request):
    deals = get_active_deals().filter(show_on_homepage=True).prefetch_related("items__product")[:20]

    return render(request, "deals/home.html", {"deals": deals})



# =====================================================
# 🔎 SEARCH
# =====================================================
def deal_search(request):

    query = request.GET.get('q', '')

    deals = get_active_deals().filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(short_description__icontains=query) |
        Q(coupon_code__icontains=query)
    )

    return render(request, "deals/search.html", {
        "deals": deals,
        "query": query
    })


# =====================================================
# 📊 CLICK TRACKING
# =====================================================
def deal_click(request, slug):
    deal = get_object_or_404(Deal, slug=slug)

    deal.clicks += 1
    deal.save(update_fields=["clicks"])

    return redirect("deal-detail", slug=deal.slug)

from django.shortcuts import render, redirect
from .forms import DealForm
from .models import Deal
from .forms import DealItemFormSet
from .forms import DealForm, DealItemFormSet

def deal_create(request):
    if request.method == "POST":
        form = DealForm(request.POST, request.FILES)

        if form.is_valid():
            deal = form.save()

            formset = DealItemFormSet(request.POST, instance=deal)

            if formset.is_valid():
                formset.save()

            return redirect('deal-list')

    else:
        form = DealForm()
        formset = DealItemFormSet()

    return render(request, 'deals/deal_form.html', {
        'form': form,
        'formset': formset
    })

# =====================================================
# 🛒 ADD DEAL TO CART (FIXED - IMPORTANT)
# =====================================================

from decimal import Decimal

def add_deal_to_cart(request, slug):
    deal = get_object_or_404(Deal.objects.prefetch_related('items__product'), slug=slug)
    cart = get_cart(request)

    created_items = 0
    total_savings = Decimal("0")

    for item in deal.items.select_related("product"):

        product = item.product

        base_price = product.final_price if hasattr(product, "final_price") else product.price

        discount_percent = deal.discount_percentage or 0

        discounted_price = base_price - (base_price * Decimal(discount_percent) / 100)

        savings = (base_price - discounted_price) * item.quantity
        total_savings += savings

        CartItem.objects.create(
            cart=cart,
            product=product,
            variant=None,
            quantity=item.quantity,
            unit_price=discounted_price   # 🔥 IMPORTANT FIX
        )

        created_items += 1

    # optional: store savings in session
    request.session["deal_savings"] = float(total_savings)

    return redirect("cart:cart_detail")
