from django.urls import path
from . import views

app_name = "customization"

urlpatterns = [
    # =========================================
    # 1. PRODUCT CUSTOMIZATION (FULL STRUCTURE)
    # Used for pizza/burger builder UI
    # =========================================
    path(
        "product/<int:product_id>/",
        views.product_customization,
        name="product_customization"
    ),

    # =========================================
    # 2. VALIDATE CUSTOMIZATION SELECTION
    # Called before adding to cart
    # =========================================
    path(
        "validate/",
        views.validate_customization,
        name="validate_customization"
    ),

    # =========================================
    # 3. SINGLE GROUP DETAIL (UI SUPPORT)
    # Optional lazy-loading for frontend
    # =========================================
    path(
        "group/<int:group_id>/",
        views.customization_group_detail,
        name="customization_group_detail"
    ),

    # =========================================
    # 4. HEALTH CHECK (DEBUG ONLY)
    # =========================================
    path(
        "health/",
        views.customization_health,
        name="customization_health"
    ),

    path(
    "product/<int:product_id>/view/",
    views.product_customization_page,
    name="product_customization_page"
),

]



# templates/
#  └── customization/
#       ├── product_customizer.html
#       ├── add_to_cart_success.html
#       ├── customization_validation_result.html
#       ├── customizer_debug.html
#       └── components/
#            ├── customization_group.html
#            └── customization_option.html