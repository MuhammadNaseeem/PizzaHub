from django.urls import path
from . import views

app_name = "core"   # ✅ ADD THIS

urlpatterns = [
    path('', views.home, name='index'),  # (recommended: index instead of home)
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('test-email/', views.test_email, name='test_email'),
]

