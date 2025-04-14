from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Appliances', 'Appliances'),
        ('Baby', 'Baby'),
        ('Clothing', 'Clothing'),
        ('Computer & Electronics', 'Computer & Electronics'),
        ('Groceries', 'Groceries'),
        ('Garden & Partio', 'Garden & Partio'),
        ('Homeware', 'Homeware'),
        ('Homekeeping', 'Homekeeping'),
        ('Outdoor & Sports', 'Outdoor & Sports'),
        ('Office Supplies & Stationary', 'Office Supplies & Stationary'),
        ('TV, Audio & Media', 'TV, Audio & Media'),        
    ]

    SUBCATEGORY_CHOICES = [
        # Appliances
        # Kitchen Appliances
        ('Refrigerators & Freezers', 'Refrigerators & Freezers'),
        ('Microwaves', 'Microwaves'),
        ('Ovens & Stoves', 'Ovens & Stoves'),
        ('Dishwashers', 'Dishwashers'),
        ('Blenders & Juicers', 'Blenders & Juicers'),
        ('Toasters & Sandwich Makers', 'Toasters & Sandwich Makers'),
        ('Coffee Machines & Kettles', 'Coffee Machines & Kettles'),
        ('Food Processors', 'Food Processors'),

        # Laundry Appliances
        ('Washing Machines', 'Washing Machines'),
        ('Tumble Dryers', 'Tumble Dryers'),
        ('Steam Irons & Garment Steamers', 'Steam Irons & Garment Steamers'),

        # Cooling & Heating
        ('Air Conditioners', 'Air Conditioners'),
        ('Fans', 'Fans'),
        ('Heaters', 'Heaters'),
        ('Electric Blankets', 'Electric Blankets'),

        # Homewares
        # Kitchen & Dining
        ('Cookware', 'Cookware'),
        ('Utensils & Cutlery', 'Utensils & Cutlery'),
        ('Dinnerware', 'Dinnerware'),
        ('Glassware', 'Glassware & Mugs'),
        ('Storage', 'Food Storage'),
        ('Appliances', 'Kitchen Appliances'),

        # Living Room
        ('cushions', 'Cushions & Throws'),
        ('curtains', 'Curtains & Blinds'),
        ('rugs', 'Rugs & Carpets'),
        ('lighting', 'Lamps & Lighting'),
        ('tables', 'Coffee/Side Tables'),
        ('wallart', 'Wall Art & Frames'),

        # Bedroom
        ('bedding', 'Bedding'),
        ('mattresses', 'Mattresses'),
        ('wardrobes', 'Wardrobes & Drawers'),
        ('lamps', 'Bedside Lamps'),
        ('blankets', 'Blankets'),
    ]

    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100, choices=SUBCATEGORY_CHOICES, blank=False, null=False)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"




class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Cart {self.cart_id} for {self.customer_id.username}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.product_id.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_item_id = models.AutoField(primary_key=True)
    cart_id = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product_id.name}"

