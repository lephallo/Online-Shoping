from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Appliances', 'Appliances'),
        ('Baby', 'Baby'),
        ('Computer & Electronics', 'Computer & Electronics'),
        ('Groceries', 'Groceries'),
        ('Homeware', 'Homeware'),
        ('TV, Audio & Media', 'TV, Audio & Media'),        
    ]

    SUBCATEGORY_CHOICES = [
        # Appliances
        ('Refrigerators & Freezers', 'Refrigerators & Freezers'),
        ('Microwaves', 'Microwaves'),
        ('Ovens & Stoves', 'Ovens & Stoves'),
        ('Steam Irons & Garment Steamers', 'Steam Irons & Garment Steamers'),
        ('Air Conditioners', 'Air Conditioners'),

        # Homewares
        ('Cookware', 'Cookware'),
        ('Dinnerware', 'Dinnerware'),
        ('Glassware', 'Glassware & Mugs'),
        ('Curtains & Blinds', 'Curtains & Blinds'),
        ('Wall Art & Frames', 'Wall Art & Frames'),
        ('Bedding', 'Bedding'),
        ('Wardrobes & Drawers', 'Wardrobes & Drawers'),

        # Baby
        ('Baby & Toddler Food', 'Baby & Toddler Food'),
        ('Baby Care', 'Baby Care'),
        ('Nappies & Wipes', 'Nappies & Wipes'),
        ('Baby Clothing', 'Baby Clothing'),

        # Computer and Electronics
        ('Computers, Laptops & Tablets', 'Computers, Laptops & Tablets'),
        ('Accessories', 'Accessories'),
        ('Powerbanks', 'Powerbanks'),
        ('Mouse, Keyboards & Speakers', 'Mouse, Keyboards & Speakers'),
        ('Cables & Connectors', 'Cables & Connectors'),


        # Groceries
        ('Fresh Produce', 'Fresh Produce'),
        ('Meet & Poultry', 'Meet & Poultry'),
        ('Bakery', 'Bakery'),
        ('Frozen Foods', 'Frozen Foods'),
        ('Snacks & Confectionery', 'Snacks & Confectionery'),

        # TV, Audio and Media
        ('Televisions', 'Televisions'),
        ('Soundbars & Speakers', 'Soundbars & Speakers'),
        ('Headphones & Earphones', 'Headphones & Earphones'),
        ('Media Players & Decoders', 'Media Players & Decoders'),
        ('TV Accessories', 'TV Accessories'),
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



class Transaction(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Mpesa', 'Mpesa'),
        ('EcoCash', 'EcoCash'),
        ('C-Pay', 'C-Pay'),
        ('PayPal', 'PayPal'),
        ('Crypto', 'Crypto'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    cart_snapshot = models.JSONField()  # Stores what was in the cart at purchase time
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    reference = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4())[:12].replace('-', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - {self.user.username} - {self.status} - {self.payment_method or 'N/A'}"





class AnonCart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    session_key = models.CharField(max_length=100, db_index=True)  # Can store UUID or Django session key
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"AnonCart {self.cart_id} for session {self.session_key}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def total_price(self):
        return sum(item.product_id.price * item.quantity for item in self.items.all())


class AnonCartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    cart_id = models.ForeignKey(AnonCart, on_delete=models.CASCADE, related_name='items')
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product_id.name} (Anon)"


class AnonTransaction(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('Mpesa', 'Mpesa'),
        ('EcoCash', 'EcoCash'),
        ('C-Pay', 'C-Pay'),
        ('PayPal', 'PayPal'),
        ('Crypto', 'Crypto'),
    ]

    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    session_key = models.CharField(max_length=100, db_index=True)
    cart_snapshot = models.JSONField()  # Stores what was in the cart at purchase time
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    created_at = models.DateTimeField(default=now)
    reference = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = str(uuid.uuid4())[:12].replace('-', '')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} - session {self.session_key} - {self.status}"