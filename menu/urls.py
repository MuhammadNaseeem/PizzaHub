from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path('', views.home, name='home'),

    path('category/<slug:slug>/', views.category_detail, name='category_detail'),

    path(
        'product/<slug:slug>/',
        views.ProductDetailView.as_view(),
        name='product_detail'
    ),  # 👈 IMPORTANT COMMA FIX HERE

    path('search/', views.search_products, name='search_products'),

    path('featured/', views.featured_products, name='featured_products'),

    path('promotions/', views.promotions, name='promotions'),
    path('promotion/<int:pk>/', views.promotion_detail, name='promotion_detail'),
    path(
    'promotion/<int:pk>/add-to-cart/',
    views.add_promotion_to_cart,
    name='add_promotion_to_cart'
),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
]
