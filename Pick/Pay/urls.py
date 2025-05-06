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
    path('admin_logout', views.admin_logout_view, name="admin_logout"),
    path('admin-login/', views.custom_login_view, name='custom_login'),

    # Customers
    path('customer-dashboard/', views.customer_dashboard, name="customer_dashboard"),
    path('appliances', views.appliances, name="appliances"),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('homeware-products', views.homeware, name="homeware"),
    path('delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('edit-product/<int:pk>/', views.delete_product, name='edit_product'),
    path('add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/reduce/', views.reduce_cart_item_quantity, name='reduce_cart_item'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('cart/history/', views.cart_history, name='cart_history'),
    path('payment-success/<uuid:transaction_id>/', views.payment_success, name="payment_success"),
    path('submit-rating/', views.submit_rating, name='submit_rating'),
    path('log-activity/', views.log_activity_view, name='log_activity'),
    path('log-activity/', views.log_user_activity, name='log_user_activity'),
    path('guest-orders', views.guest_orders_page, name="guest_orders"),

    path('cart/pay/', views.make_payment, name='make_payment'),
    path('guest/cart/pay/', views.guest_make_payment, name='guest_make_payment'),
    path('cart/process-payment/', views.process_payment, name='process_payment'),
    path('guest/cart/process-payment/', views.guest_process_payment, name='guest_process_payment'),
    path('cart/success/<str:reference>/', views.guest_transaction_success, name='guest_transaction_success'),
    path('guest/cart/success/<str:reference>/', views.transaction_success, name='transaction_success'),

    path('groceries-at-pick-and-pay', views.groceries, name="groceries"),
    path('baby-products', views.baby, name="baby"),
    path('tv-audio-media', views.televisions, name="tv"),
    path('computer-and-electronics', views.computer, name="computer"),

    # Managers
    path('admin-dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('product-management', views.product_management, name="product_management"),
    path('view-all-transactions', views.all_transactions_view, name='all_transactions'),
    path('sales-report', views.sales_report_view, name="sales_report"),

    path('delete-cart-item/<int:product_id>/', views.delete_cart_item_again, name='delete_cart_item_again'),

]