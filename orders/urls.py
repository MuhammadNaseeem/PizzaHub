from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [


    path("", views.order_list, name="order_list"),
    path("<int:pk>/", views.order_detail, name="order_detail"),  # ✅ ADD THIS

    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.checkout_success, name="checkout_success"),
    path("delete/<int:pk>/", views.order_delete, name="order_delete"),
]


