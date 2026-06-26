from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import (
    SiteSettings,
    HeroBanner,
    Feature,
    Testimonial,
    FAQ,
    ContactMessage,
    EmailLog,
)

from deals.models import Deal
from menu.models import Product
from core.utils.email import send_html_email


# =====================================================
# HOME PAGE
# =====================================================
def home(request):
    site_settings = SiteSettings.objects.first()

    deals = Deal.objects.filter(
        is_active=True,
        show_on_homepage=True
    ).order_by('-priority', '-is_featured')[:6]

    products = Product.objects.filter(
        is_available=True
    ).order_by('-id')[:8]

    context = {
        'site_settings': site_settings,
        'hero': HeroBanner.objects.filter(is_active=True),
        'features': Feature.objects.all(),
        'testimonials': Testimonial.objects.all(),
        'deals': deals,
        'products': products,
    }

    return render(request, 'core/index.html', context)


# =====================================================
# ABOUT PAGE
# =====================================================
def about(request):
    site_settings = SiteSettings.objects.first()

    context = {
        'site_settings': site_settings,
        'features': Feature.objects.all(),
        'testimonials': Testimonial.objects.all(),
    }

    return render(request, 'core/about.html', context)


# =====================================================
# CONTACT PAGE
# =====================================================
def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        # 📧 Send email to admin
        send_mail(
            subject=f"Contact: {subject}",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        # 🧾 Log email
        EmailLog.objects.create(
            email=email,
            subject=subject,
            message=message,
            status="sent"
        )

        messages.success(request, "Message sent successfully!")

        # Redirect back to contact page
        return redirect('core:contact')

    return render(request, 'core/contact.html')

# =====================================================
# FAQ PAGE
# =====================================================
def faq(request):
    site_settings = SiteSettings.objects.first()

    context = {
        'site_settings': site_settings,
        'faqs': FAQ.objects.all().order_by('sort_order'),
    }

    return render(request, 'core/faq.html', context)


# =====================================================
# TEST EMAIL (DEV ONLY)
# =====================================================
def test_email(request):

    html_message = render_to_string("emails/order_confirmation.html", {
        "name": "Muhammad Naseem"
    })

    send_html_email(
        subject="🍕 Order Confirmed",
        text_message="Your order is confirmed",
        html_message=html_message,
        recipient="test@gmail.com"
    )

    return HttpResponse("Email sent successfully 🚀")







# python manage.py startapp core
# python manage.py startapp accounts
# python manage.py startapp menu
# python manage.py startapp cart
# python manage.py startapp orders  i will use in this app, from core.utils.email import send_html_email
# python manage.py startapp coupons
# python manage.py startapp reviews
# python manage.py startapp dashboard



# for deleting, rm -rf ~/PizzaHub

# cd ~/PizzaHub
# ls
# https://github.com/MuhammadNaseeem/PizzaHub.git
# workon pizzahubenv
# mkvirtualenv --python=/usr/bin/python3.13 pizzahubenv
# pip install -r requirements.txt
# nano .env
# python manage.py migrate
# mkdir -p ~/PizzaHub/static


# on pythonanywhere
# rm db.sqlite3
# cp db.sqlite3 db.sqlite3.backup
# ls -lh db.sqlite3

# for images 
#  "C:\Users\Muhammad Naseem\Desktop\ECOM-PIZZA\db.sqlite3" muhammadnaseem@ssh.pythonanywhere.com:/home/muhammadnaseem/PizzaHub/
# scp -r "C:\Users\Muhammad Naseem\Desktop\ECOM-PIZZA\customization" muhammadnaseem@ssh.pythonanywhere.com:/home/muhammadnaseem/PizzaHub/media/


# for generating new secret key
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"