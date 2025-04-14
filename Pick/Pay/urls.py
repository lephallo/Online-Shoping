from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name="welcome"),
    path('home', views.base, name="home"),
    path('about-us', views.about, name="about_us"),

    # Authentication
    path('customer-login', views.login_view, name="login"),
    path('customer-account-registeration', views.signup_view, name="signup"),
    path('logout', views.logout_view, name="logout"),

    # Customers
    path('customer-dashboard/', views.customer_dashboard, name="customer_dashboard"),
    path('appliances', views.appliances, name="appliances"),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('homeware-products', views.homeware, name="homeware"),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),

    # Managers
    path('admin-dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('product-management', views.product_management, name="product_management"),
]