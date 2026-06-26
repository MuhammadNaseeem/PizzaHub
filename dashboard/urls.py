from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),

    path('products/', views.products, name='dashboard_products'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),

    path('orders/', views.orders, name='dashboard_orders'),
    path('customers/', views.customers, name='dashboard_customers'),
    path('coupons/', views.coupons, name='dashboard_coupons'),

    path('reviews/', views.reviews, name='dashboard_reviews'),
    path('reviews/<int:pk>/approve/', views.approve_review, name='approve_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),

    path('messages/', views.messages_page, name='dashboard_messages'),
    path('messages/delete/<int:id>/', views.delete_message, name='delete_message'),
    path('messages/read/<int:id>/', views.mark_message_read, name='mark_message_read'),
]


