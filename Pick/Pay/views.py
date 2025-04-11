from django.shortcuts import render
from django.shortcuts import redirect

from .models import Product

from .forms import ProductForm



def base(request):
    # Fetch all categories
    categories = Product.objects.values('category').distinct()

    # Initialize the dictionary to store products by category
    products_by_category = {}

    for category in categories:
        # Get the latest 4 products for each category
        latest_products = Product.objects.filter(category=category['category']) \
                                        .order_by('-created_at')[:4]

        # Add these products to the dictionary
        products_by_category[category['category']] = latest_products

    return render(request, 'pay/landing_pages/base.html', {
        'products_by_category': products_by_category
    })




def about(request):
    return render(request, 'pay/landing_pages/about.html')


# Managers dashboard
def admin_dashboard(request):
    return render(request, 'pay/managers/dashboard.html')



def product_management(request):
    # If the form is submitted via POST
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        # Validate form data
        if form.is_valid():
            form.save()  # Save the new product to the database
            return redirect('product_management')  # Redirect back to the product management page to see the new product
    else:
        form = ProductForm()  # If GET request, initialize a blank form

    # Fetch all products from the database to display in the table
    products = Product.objects.all()

    # Render the product management page with the form and products
    return render(request, 'pay/managers/product_management.html', {
        'form': form,
        'products': products,
    })




