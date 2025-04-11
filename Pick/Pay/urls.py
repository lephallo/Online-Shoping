from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name="welcome"),
    path('home', views.base, name="home"),
    path('about-us', views.about, name="about_us"),

    # Managers
    path('admin-dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('product-management', views.product_management, name="product_management"),
]