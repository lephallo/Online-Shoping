from django.contrib import admin
from .models import Product
from .models import Profile
from .models import Cart
from .models import CartItem

# Register the Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'price', 'stock', 'is_featured', 'created_at')
    list_filter = ('category', 'subcategory', 'is_featured')
    search_fields = ('name', 'description', 'category', 'subcategory')

admin.site.register(Product, ProductAdmin)

# Register the Profile model
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact', 'location', 'image')
    search_fields = ('user__username', 'contact', 'location')

admin.site.register(Profile, ProfileAdmin)

# Register the Cart model
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'created_at', 'total_items', 'total_price')
    search_fields = ('customer_id__username',)

admin.site.register(Cart, CartAdmin)

# Register the CartItem model
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'product_id', 'quantity')
    search_fields = ('product_id__name', 'cart_id__customer_id__username')

admin.site.register(CartItem, CartItemAdmin)
