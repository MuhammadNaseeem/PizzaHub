from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def login_view(request):

    if request.user.is_authenticated:
        return redirect('core:index')

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🔥 IMPORTANT: MERGE CART HERE
            merge_cart(request, user)

            return redirect('core:index')

        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'accounts/login.html')




def signup_view(request):

    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.save()

        messages.success(request, "Account created successfully!")
        return redirect('login')

    return render(request, 'accounts/signup.html')

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'accounts/profile.html')

def logout_view(request):
    logout(request)
    return redirect('login')


from cart.models import Cart, CartItem

from django.db import transaction

def merge_cart(request, user):

    session_id = request.session.session_key

    if not session_id:
        return

    try:
        guest_cart = Cart.objects.get(session_id=session_id, is_active=True)
    except Cart.DoesNotExist:
        return

    user_cart, created = Cart.objects.get_or_create(
        user=user,
        is_active=True
    )

    # 🔥 SAFE TRANSFER
    with transaction.atomic():

        for item in guest_cart.items.all():
            item.cart = user_cart
            item.save()

        guest_cart.delete()