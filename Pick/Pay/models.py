from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Appliances', 'appliances'),
        ('Baby', 'baby'),
        ('Clothing', 'Clothing'),
        ('Computer & Electronics', 'Computer & Electronics'),
        ('Groceries', 'Groceries'),
        ('Garden & Partio', 'garden & partio'),
        ('Homeware', 'homeware'),
        ('Homekeeping', 'homekeeping'),
        ('Outdoor & Sports', 'outdoor & sports'),
        ('Office Supplies & Stationary', 'office & stationary'),
        ('TV, Audio & Media', 'tv, audio & media'),        
    ]


    product_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
