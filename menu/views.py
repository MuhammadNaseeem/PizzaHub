
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg
from django.views.generic import DetailView

from .models import Category, Product, Promotion, ProductImage, ProductReview, ProductVariant, Addon

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product, ProductReview


# =========================
# HOME (MENU LANDING)
# =========================
def home(request):

    categories = Category.objects.filter(is_active=True).order_by('sort_order')

    featured_products = Product.objects.filter(
        is_featured=True,
        is_available=True
    ).select_related('category')[:8]

    latest_products = Product.objects.filter(
        is_available=True
    ).select_related('category')[:12]

    promotions = Promotion.objects.filter(
        is_active=True
    )

    return render(request, 'menu/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
        'promotions': promotions,
    })


# =========================
# CATEGORY PRODUCTS
# =========================
def category_detail(request, slug):

    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    products = Product.objects.filter(
        category=category,
        is_available=True
    ).prefetch_related('images', 'variants', 'tags')

    return render(request, 'menu/category_detail.html', {
        'category': category,
        'products': products,
    })


# =========================
# PRODUCT DETAIL
# =========================
from django.views.generic import DetailView
from django.db.models import Avg, Count
from .models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = "menu/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(
            is_available=True
        ).select_related(
            "category"
        ).prefetch_related(
            "images",
            "variants",
            "tags",
            "reviews__user"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        product = self.object

        # =========================
        # IMAGES (SAFE + CLEAN)
        # =========================
        primary_image = product.images.filter(is_primary=True).first()

        primary_image_url = None
        if primary_image:
            primary_image_url = primary_image.image.url
        elif product.thumbnail:
            primary_image_url = product.thumbnail.url

        images = product.images.all().order_by("sort_order")

        # =========================
        # VARIANTS
        # =========================
        variants = product.variants.filter(is_active=True).order_by("price")

        # =========================
        # REVIEWS (OPTIMIZED)
        # =========================
        reviews = product.reviews.select_related("user").order_by("-created_at")

        review_stats = product.reviews.aggregate(
            avg_rating=Avg("rating"),
            review_count=Count("id")
        )

        avg_rating = review_stats["avg_rating"] or 0
        review_count = review_stats["review_count"]

        # =========================
        # TAGS
        # =========================
        tags = product.tags.all()

        # =========================
        # STOCK STATUS (SMART)
        # =========================
        if product.stock_quantity > 10:
            stock_status = "In Stock"
        elif product.stock_quantity > 0:
            stock_status = "Low Stock"
        else:
            stock_status = "Out of Stock"

        # =========================
        # PRICE LOGIC
        # =========================
        final_price = product.sale_price or product.base_price

        discount_percent = None
        if product.sale_price and product.base_price:
            discount_percent = round(
                ((product.base_price - product.sale_price) / product.base_price) * 100
            )

        # =========================
        # SEO
        # =========================
        seo_title = product.meta_title or product.name
        seo_description = product.meta_description or product.short_description

        # =========================
        # CONTEXT
        # =========================
        context.update({
            "primary_image_url": primary_image_url,
            "images": images,
            "variants": variants,
            "reviews": reviews,

            "avg_rating": round(avg_rating, 1),
            "review_count": review_count,

            "tags": tags,
            "stock_status": stock_status,

            "final_price": final_price,
            "discount_percent": discount_percent,

            "seo_title": seo_title,
            "seo_description": seo_description,
        })

        return context
    
        

# =========================
# SEARCH PRODUCTS
# =========================
from django.db.models import Q, Case, When, Value, IntegerField
from django.shortcuts import render
from .models import Product


def search_products(request):

    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', '')

    products = Product.objects.filter(is_available=True).select_related('category').prefetch_related('tags')

    # =========================
    # SEARCH LOGIC (SMART RANKING)
    # =========================
    if query:

        products = products.annotate(
            relevance=Case(
                When(name__icontains=query, then=Value(3)),
                When(short_description__icontains=query, then=Value(2)),
                When(description__icontains=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )
        ).filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct().order_by('-relevance')

    # =========================
    # FILTER BY TAG
    # =========================
    if tag:
        products = products.filter(tags__name__iexact=tag)

    # =========================
    # FILTER BY CATEGORY
    # =========================
    if category:
        products = products.filter(category__slug=category)

    # =========================
    # SORTING (LIKE ECOM SITES)
    # =========================
    if sort == 'price_low':
        products = products.order_by('base_price')

    elif sort == 'price_high':
        products = products.order_by('-base_price')

    elif sort == 'newest':
        products = products.order_by('-created_at')

    elif sort == 'featured':
        products = products.order_by('-is_featured', '-created_at')

    # =========================
    # EMPTY SEARCH HANDLING
    # =========================
    if not query and not tag:
        products = Product.objects.none()

    return render(request, 'menu/search.html', {
        'products': products,
        'query': query,
        'tag': tag,
        'category': category,
        'sort': sort,
    })

from django.shortcuts import render
from django.db.models import Case, When, Value, IntegerField
from decimal import Decimal

from customization.models import CustomizationRule
from .models import Product


def featured_products(request):

    sort = request.GET.get('sort', '')
    category = request.GET.get('category', '')

    products = Product.objects.filter(
        is_featured=True,
        is_available=True
    ).select_related('category').prefetch_related('customization_groups__group')

    if category:
        products = products.filter(category__slug=category)

    # ranking boost
    products = products.annotate(
        boost=Case(
            When(average_rating__gte=4.5, then=Value(3)),
            When(average_rating__gte=4.0, then=Value(2)),
            When(total_orders__gte=10, then=Value(2)),
            default=Value(1),
            output_field=IntegerField()
        )
    )

    rules = CustomizationRule.objects.filter(
        is_active=True,
        rule_type="discount",
        discount_type="percent"
    )

    product_list = []

    for product in products:

        product_groups = set(
            product.customization_groups.values_list("group_id", flat=True)
        )

        best_discount = Decimal("0")

        for rule in rules:
            if rule.trigger_group_id in product_groups:
                best_discount = max(best_discount, rule.discount_amount)

        # ✅ SAFE VALUE FOR TEMPLATE
        product.discount_percent = best_discount if best_discount > 0 else 0\

        product_list.append(product)

    # sorting
    if sort == 'top_rated':
        product_list.sort(key=lambda x: (-x.average_rating, -x.boost))

    elif sort == 'popular':
        product_list.sort(key=lambda x: (-x.total_orders, -x.boost))

    elif sort == 'newest':
        product_list.sort(key=lambda x: -x.created_at.timestamp())

    else:
        product_list.sort(key=lambda x: (-x.is_featured, -x.boost))

    return render(request, 'menu/featured_products.html', {
        'featured_products': product_list,
        'sort': sort,
        'category': category,
    })







from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages

from .models import Promotion
from cart.models import Cart, CartItem  # adjust if your cart app name differs


def promotions(request):
    now = timezone.now()
    sort = request.GET.get('sort', '')

    promotions_qs = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )

    if sort == 'ending_soon':
        promotions_qs = promotions_qs.order_by('end_date')

    elif sort == 'newest':
        promotions_qs = promotions_qs.order_by('-start_date')

    elif sort == 'highest_discount':
        promotions_qs = promotions_qs.order_by('-discount_percentage')

    else:
        promotions_qs = promotions_qs.order_by('-start_date')

    return render(request, 'menu/promotions.html', {
        'promotions': promotions_qs,
        'sort': sort,
    })


def promotion_detail(request, pk):
    now = timezone.now()

    promotion = get_object_or_404(
        Promotion,
        pk=pk,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )

    return render(request, 'menu/promotion.html', {
        'promotion': promotion
    })


# =========================
# ADD PROMOTION TO CART
# =========================
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Promotion

@login_required
def add_promotion_to_cart(request, pk):

    promotion = get_object_or_404(Promotion, pk=pk)

    request.session['promotion_id'] = promotion.id
    request.session['discount_percentage'] = promotion.discount_percentage

    return redirect('cart:cart_detail')




@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    review = ProductReview.objects.filter(
        product=product,
        user=request.user
    ).first()

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if rating and comment:
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    "rating": rating,
                    "comment": comment
                }
            )

            messages.success(request, "Review submitted successfully!")
        else:
            messages.error(request, "Please fill all fields.")

        return redirect("menu:product_detail", slug=product.slug)

    return redirect("menu:product_detail", slug=product.slug)



