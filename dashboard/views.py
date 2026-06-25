from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count

from orders.models import Order
from menu.models import Product, ProductReview
from core.models import ContactMessage


def dashboard_home(request):

    orders = Order.objects.all()

    total_products = Product.objects.count()
    total_orders = orders.count()
    total_customers = User.objects.count()

    # Messages
    total_messages = ContactMessage.objects.count()

    unread_messages = ContactMessage.objects.filter(
        status='new'
    ).count()

    # Reviews
    total_reviews = ProductReview.objects.count()

    recent_reviews = ProductReview.objects.select_related(
        'user',
        'product'
    ).order_by('-created_at')[:5]

    # Orders
    recent_orders = orders.order_by('-id')[:5]

    # Chart Data
    order_status_data = (
        orders.values('status')
        .annotate(total=Count('id'))
    )

    labels = [item['status'] for item in order_status_data]
    data = [item['total'] for item in order_status_data]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,

        'total_messages': total_messages,
        'unread_messages': unread_messages,

        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,

        'recent_orders': recent_orders,

        'chart_labels': labels,
        'chart_data': data,
    }

    return render(
        request,
        'dashboard/dashboard.html',
        context
    )



# ---------------- PRODUCTS ----------------
from django.core.paginator import Paginator
from django.db.models import Q

def products(request):

    query = request.GET.get('q')

    products = Product.objects.all().order_by('-id')

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/products.html', {
        'page_obj': page_obj,
        'query': query,
    })


def delete_product(request, id):
    if request.method == "POST":
        Product.objects.filter(id=id).delete()
        return JsonResponse({'success': True})


# ---------------- ORDERS ----------------

def orders(request):

    status = request.GET.get('status')

    orders = Order.objects.select_related('user').all().order_by('-id')

    if status:
        orders = orders.filter(status=status)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/orders.html', {
        'page_obj': page_obj,
        'status': status,
    })


# ---------------- CUSTOMERS ----------------
def customers(request):

    query = request.GET.get('q')

    users = User.objects.all().order_by('-id')

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query)
        )

    paginator = Paginator(users, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/customers.html', {
        'page_obj': page_obj,
        'query': query,
    })

# ---------------- COUPONS ----------------
def coupons(request):

    context = {
        'coupons': Coupon.objects.all().order_by('-id')
    }

    return render(request, 'dashboard/coupons.html', context)


# ---------------- REVIEWS ----------------
def reviews(request):

    context = {
        'reviews': Review.objects.select_related('user', 'product').all().order_by('-id')
    }

    return render(request, 'dashboard/reviews.html', context)


# ---------------- MESSAGES ----------------
from django.core.paginator import Paginator
from django.db.models import Q

def messages_page(request):

    query = request.GET.get('q')

    messages = ContactMessage.objects.all().order_by('-created_at')

    if query:
        messages = messages.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query)
        )

    paginator = Paginator(messages, 10)

    page_obj = paginator.get_page(
        request.GET.get('page')
    )

    context = {
        'page_obj': page_obj,
        'new_messages': ContactMessage.objects.filter(status='new').count(),
        'read_messages': ContactMessage.objects.filter(status='read').count(),
        'total_messages': ContactMessage.objects.count(),
    }

    return render(
        request,
        'dashboard/messages.html',
        context
    )



from django.shortcuts import redirect, get_object_or_404
from core.models import ContactMessage

def delete_message(request, id):
    message = get_object_or_404(ContactMessage, id=id)

    if request.method == "POST":
        message.delete()

    return redirect('dashboard:dashboard_messages')


def mark_message_read(request, id):
    message = get_object_or_404(ContactMessage, id=id)

    message.status = 'read'
    message.save()

    return redirect('dashboard:dashboard_messages')



from django.shortcuts import redirect

def add_product(request):
    return redirect('/admin/menu/product/add/')


from django.shortcuts import redirect

def add_deal(request):
    return redirect('/admin/deals/product/add/')


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from menu.models import ProductReview


def reviews(request):
    reviews = ProductReview.objects.select_related(
        'user',
        'product'
    ).order_by('-created_at')

    approved_count = ProductReview.objects.filter(
        is_approved=True
    ).count()

    average_rating = ProductReview.objects.aggregate(
        Avg('rating')
    )['rating__avg'] or 0

    return render(
        request,
        'dashboard/reviews.html',
        {
            'reviews': reviews,
            'approved_count': approved_count,
            'average_rating': round(average_rating, 1),
        }
    )


def approve_review(request, pk):
    review = get_object_or_404(ProductReview, pk=pk)

    review.is_approved = True
    review.save()

    return redirect('dashboard:dashboard_reviews')


def delete_review(request, pk):
    review = get_object_or_404(ProductReview, pk=pk)

    review.delete()

    return redirect('dashboard:dashboard_reviews')

