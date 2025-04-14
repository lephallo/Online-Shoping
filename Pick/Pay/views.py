from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.http import JsonResponse

from .models import Product
from .models import Profile
from .models import Cart
from .models import CartItem

from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm



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


def admin_dashboard(request):
    low_stock_threshold = 10
    
    # Corrected the condition syntax
    if 1 <= low_stock_threshold <= 10:
        low_stock_count = Product.objects.filter(stock__lt=low_stock_threshold, stock__gt=0).count()
    else:
        low_stock_count = 0  # Ensure variable is defined if condition is False

    out_of_stock_count = Product.objects.filter(stock=0).count()
    total_attention_items = low_stock_count + out_of_stock_count

    context = {
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_attention_items": total_attention_items,
        "user": request.user, 
    }

    return render(request, 'pay/managers/dashboard.html', context)



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



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login') 
    else:
        form = SignUpForm()
    return render(request, 'pay/auth/cus_signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = LoginForm()
    return render(request, 'pay/auth/cus_login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')



def customer_dashboard(request):
    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]

    return render(request, 'pay/customer/dashboard.html', {
        'featured_products': featured_products,
    })





def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_management')





def appliances(request):
    # Filter all Appliance products
    appliances = Product.objects.filter(category='Appliances')

    # Group products dynamically by subcategory
    grouped_appliances = {}
    for product in appliances:
        subcat = product.subcategory or "Other"
        grouped_appliances.setdefault(subcat, []).append(product)

    # Prepare data for rendering
    appliance_sections = []
    for subcategory_name, products in grouped_appliances.items():
        appliance_sections.append({
            'name': subcategory_name,
            'products': products
        })

    context = {
        'appliance_sections': appliance_sections
    }

    return render(request, 'pay/products/appliances.html', context)



@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user

        username = request.POST.get('username')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        location = request.POST.get('location')

        full_name = request.POST.get('full_name', '').strip()
        if full_name:
            parts = full_name.split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else ''
        else:
            first_name = user.first_name
            last_name = user.last_name

        if not username:
            messages.error(request, "Username is required.")
            return redirect('customer_dashboard')

        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Safely get or create the profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.contact = contact
        profile.location = location
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('customer_dashboard')



def homeware(request):
    # Filter all Appliance products
    homeware = Product.objects.filter(category='Homeware')

    # Group products dynamically by subcategory
    grouped_homeware = {}
    for product in homeware:
        subcat = product.subcategory or "Other"
        grouped_homeware.setdefault(subcat, []).append(product)

    # Prepare data for rendering
    homeware_sections = []
    for subcategory_name, products in grouped_homeware.items():
        homeware_sections.append({
            'name': subcategory_name,
            'products': products
        })

    context = {
        'homeware_sections': homeware_sections
    }

    return render(request, 'pay/products/homeware.html', context)


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        # Force evaluation of request.user
        user = request.user
        user_id = user.id

        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found'}, status=404)

        # Get or create the cart for the logged-in user
        cart, created = Cart.objects.get_or_create(customer_id=request.user, defaults={'created_at': now()})

        # Get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart_id=cart,
            product_id=product,
            defaults={
                'quantity': quantity,
                'user_id': user_id  # Important! This prevents the user_id IntegrityError
            }
        )

        # If already exists, just update quantity
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Cart summary
        cart_items = CartItem.objects.filter(cart_id=cart)
        total_items = sum(item.quantity for item in cart_items)
        total_price = sum(item.product_id.price * item.quantity for item in cart_items)

        return JsonResponse({
            'success': True,
            'cart_items': [
                {
                    'name': item.product_id.name,
                    'price': item.product_id.price,
                    'quantity': item.quantity,
                    'total_price': item.product_id.price * item.quantity,
                    'product_id': item.product_id.product_id,
                } for item in cart_items
            ],
            'total_items': total_items,
            'total_price': str(total_price),
        })

    return JsonResponse({'success': False}, status=400)


@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        try:
            cart = Cart.objects.get(customer_id=request.user)
            product = Product.objects.get(product_id=product_id)
            cart_item = CartItem.objects.get(cart_id=cart, product_id=product)

            if cart_item.quantity > 1:
                # Decrease the quantity by 1
                cart_item.quantity -= 1
                cart_item.save()
            else:
                # Delete the item completely if quantity is 1
                cart_item.delete()

            # Update cart summary
            cart_items = CartItem.objects.filter(cart_id=cart)
            total_items = sum(item.quantity for item in cart_items)
            total_price = sum(item.product_id.price * item.quantity for item in cart_items)

            return JsonResponse({
                'success': True,
                'cart_items': [
                    {
                        'name': item.product_id.name,
                        'price': item.product_id.price,
                        'quantity': item.quantity,
                        'total_price': item.product_id.price * item.quantity,
                        'product_id': item.product_id.product_id,
                    } for item in cart_items
                ],
                'total_items': total_items,
                'total_price': str(total_price),
            })

        except (Cart.DoesNotExist, Product.DoesNotExist, CartItem.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Item not found in cart'}, status=404)

    return JsonResponse({'success': False}, status=400)




def cart_item_count(request):
    if request.user.is_authenticated:
        count = CartItem.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'cart_count': count}



