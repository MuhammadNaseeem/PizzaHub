from django.urls import path
from . import views

app_name = 'deals'   # ✅ ADD THIS

urlpatterns = [
    path('', views.deal_list, name='deal-list'),
    path('add/', views.deal_create, name='deal-create'),
    path('featured/', views.featured_deals, name='featured-deals'),
    path('flash/', views.flash_deals, name='flash-deals'),
    path('home/', views.home_deals, name='home-deals'),
    path('search/', views.deal_search, name='deal-search'),
    path('click/<slug:slug>/', views.deal_click, name='deal-click'),

    # DETAIL
    path('<slug:slug>/', views.deal_detail, name='deal-detail'),

    path('deal/add-to-cart/<slug:slug>/', views.add_deal_to_cart, name='deal-add-to-cart'),
]

