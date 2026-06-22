from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('products/', views.products, name='dashboard_products'),
    path('orders/', views.orders, name='dashboard_orders'),
    path('customers/', views.customers, name='dashboard_customers'),
    path('coupons/', views.coupons, name='dashboard_coupons'),
    path('reviews/', views.reviews, name='dashboard_reviews'),
    path('messages/', views.messages_page, name='dashboard_messages'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),
]