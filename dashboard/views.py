from django.shortcuts import render
from django.contrib.auth.models import User

# from menu.models import Product
# from orders.models import Order
from core.models import ContactMessage
from menu.models import Review
from menu.models import Coupon

from django.http import JsonResponse
from menu.models import Product


# ---------------- DASHBOARD HOME ----------------
from django.db.models import Count
from cart.models import Order
from menu.models import Product
from django.contrib.auth.models import User

def dashboard_home(request):

    orders = Order.objects.all()

    # Simple stats
    total_products = Product.objects.count()
    total_orders = orders.count()
    total_customers = User.objects.count()

    # Chart data (last 7 orders by status)
    order_status_data = orders.values('status').annotate(total=Count('id'))

    labels = [i['status'] for i in order_status_data]
    data = [i['total'] for i in order_status_data]

    return render(request, 'dashboard/dashboard.html', {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'chart_labels': labels,
        'chart_data': data,
    })


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
def messages_page(request):

    messages_list = ContactMessage.objects.all().order_by('-id')

    paginator = Paginator(messages_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/messages.html', {
        'page_obj': page_obj,
    })


