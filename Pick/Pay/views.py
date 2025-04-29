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
import json
from collections import Counter
from django.contrib.auth.models import Group
from functools import wraps
import uuid
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models import Count
from django.db.models import Avg
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Product
from .models import Profile
from .models import Cart
from .models import CartItem
from .models import Transaction

from .mongo import save_rating
from .mongo import log_activity 
from .mongo import ratings_collection

from .forms import ProductForm
from .forms import SignUpForm
from .forms import LoginForm



ALLOWED_GROUPS = ['Operations Manager', 'Inventory Manager', 'Store Manager']

def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.groups.filter(name__in=ALLOWED_GROUPS).exists():
                login(request, user)
                return redirect('admin_dashboard')  # Use your URL name
            else:
                messages.error(request, 'You do not have access to the admin dashboard.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'pay/auth/admin_login.html')




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




def in_allowed_groups(user):
    return user.groups.filter(name__in=ALLOWED_GROUPS).exists()



def group_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('custom_login')  # custom login URL name
        if not in_allowed_groups(request.user):
            return redirect('custom_login')  # or a 403 page
        return view_func(request, *args, **kwargs)
    return _wrapped_view



# @login_required(login_url='custom_login')
@group_required
def admin_dashboard(request):
    low_stock_threshold = 10

    # Stock alerts
    if 1 <= low_stock_threshold <= 10:
        low_stock_count = Product.objects.filter(stock__lt=low_stock_threshold, stock__gt=0).count()
    else:
        low_stock_count = 0

    out_of_stock_count = Product.objects.filter(stock=0).count()
    total_attention_items = low_stock_count + out_of_stock_count

    # MongoDB: Ratings Analysis
    all_ratings = list(ratings_collection.find({}))

    rating_counts = Counter([r['product_id'] for r in all_ratings])
    five_star_counts = Counter([r['product_id'] for r in all_ratings if r['rating'] == 5])

    most_rated = rating_counts.most_common(1)[0] if rating_counts else (None, 0)
    least_rated = min(rating_counts.items(), key=lambda x: x[1]) if rating_counts else (None, 0)
    most_five_star = five_star_counts.most_common(1)[0] if five_star_counts else (None, 0)

    def get_product_name(product_id):
        try:
            # Skip non-integer IDs
            if not str(product_id).isdigit():
                return "Unknown Product"
            product = Product.objects.get(pk=int(product_id))
            return product.name
        except Product.DoesNotExist:
            return "Unknown Product"


    # Revenue grouped by day for successful transactions
    revenue_data = (
        Transaction.objects.filter(status='success')
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total_revenue=Sum('total_amount'))
        .order_by('day')
    )

    # Prepare for Chart.js
    labels = [entry['day'].strftime('%Y-%m-%d') for entry in revenue_data]
    data = [float(entry['total_revenue']) for entry in revenue_data]

    
    today = now().date()
    current_month = today.month
    current_year = today.year
    current_week_start = today - timedelta(days=today.weekday())  # Monday
    last_week_start = current_week_start - timedelta(days=7)
    last_week_end = current_week_start - timedelta(days=1)


    # Sum of successful transactions made today
    sales_today = (
        Transaction.objects.filter(status='success', created_at__date=today)
        .aggregate(total=Sum('total_amount'))
        .get('total') or 0
    )

    
    # Monthly Revenue
    monthly_revenue = (
        Transaction.objects.filter(
            status='success',
            created_at__year=current_year,
            created_at__month=current_month
        )
        .aggregate(total=Sum('total_amount'))
        .get('total') or 0
    )

        # Weekly comparison
    this_week_revenue = (
        Transaction.objects.filter(
            status='success',
            created_at__date__gte=current_week_start,
            created_at__date__lte=today
        )
        .aggregate(total=Sum('total_amount'))
        .get('total') or 0
    )

    last_week_revenue = (
        Transaction.objects.filter(
            status='success',
            created_at__date__gte=last_week_start,
            created_at__date__lte=last_week_end
        )
        .aggregate(total=Sum('total_amount'))
        .get('total') or 0
    )

    # Calculate Percentage Change (Avoid division by zero)
    if last_week_revenue:
        week_change_percentage = ((this_week_revenue - last_week_revenue) / last_week_revenue) * 100
    else:
        week_change_percentage = 0


    context = {
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_attention_items": total_attention_items,
        "user": request.user,
        "most_rated_product": {
            "name": get_product_name(most_rated[0]),
            "count": most_rated[1]
        },
        "least_rated_product": {
            "name": get_product_name(least_rated[0]),
            "count": least_rated[1]
        },
        "most_five_star_product": {
            "name": get_product_name(most_five_star[0]),
            "count": most_five_star[1]
        },
        'sales_today': sales_today,
        'monthly_revenue': monthly_revenue,
        'this_week_revenue': this_week_revenue,
        'last_week_revenue': last_week_revenue,
        'week_change_percentage': week_change_percentage,
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in revenue_data],
        'data': [float(entry['total_revenue']) for entry in revenue_data],
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


def is_customer(user):
    return user.groups.filter(name='Customer').exists()



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Add user to Customer group
            customer_group, created = Group.objects.get_or_create(name='Customer')
            user.groups.add(customer_group)

            return redirect('login') 
    else:
        form = SignUpForm()
    return render(request, 'pay/auth/cus_signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if is_customer(user):
                login(request, user)
                return redirect('customer_dashboard')
            else:
                return redirect('customer_login')  # or reload login page with error
    else:
        form = LoginForm()
    return render(request, 'pay/auth/cus_login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('login')



def admin_logout_view(request):
    logout(request)
    return redirect('custom_login')




@login_required(login_url='login')  
def customer_dashboard(request):
    if not is_customer(request.user):
        messages.error(request, "Access denied: You do not belong to the Customer group.")
        return redirect('login') 

    featured_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]

    context = {
        'featured_products': featured_products,
        'user': request.user
    }

    return render(request, 'pay/customer/dashboard.html', context) 



def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return redirect('product_management')




def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_management')  # or wherever your product list lives
    else:
        form = ProductForm(instance=product)
    





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




@csrf_exempt
def reduce_cart_item_quantity(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        try:
            cart_item = CartItem.objects.get(pk=item_id)
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()
            return JsonResponse({'success': True, 'quantity': cart_item.quantity if cart_item.quantity > 0 else 0})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})



def baby(request):
    # Filter all Appliance products
    appliances = Product.objects.filter(category='Baby')

    # Group products dynamically by subcategory
    grouped_appliances = {}
    for product in appliances:
        subcat = product.subcategory or "Other"
        grouped_appliances.setdefault(subcat, []).append(product)

    # Prepare data for rendering
    baby_sections = []
    for subcategory_name, products in grouped_appliances.items():
        baby_sections.append({
            'name': subcategory_name,
            'products': products
        })

    context = {
        'baby_sections': baby_sections
    }

    return render(request, 'pay/products/baby.html', context)



def computer(request):
    # Filter all Appliance products
    appliances = Product.objects.filter(category='Computer & Electronics')

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

    return render(request, 'pay/products/computer.html', context)



def groceries(request):
    # Filter all Appliance products
    appliances = Product.objects.filter(category='Groceries')

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

    return render(request, 'pay/products/groceries.html', context)



def televisions(request):
    # Filter all Appliance products
    digital_appliances = Product.objects.filter(category='TV, Audio & Media')

    # Group products dynamically by subcategory
    grouped_by_digitals = {}
    for product in digital_appliances:
        subcat = product.subcategory or "Other"
        grouped_by_digitals.setdefault(subcat, []).append(product)

    # Prepare data for rendering
    appliance_sections = []
    for subcategory_name, products in grouped_by_digitals.items():
        appliance_sections.append({
            'name': subcategory_name,
            'products': products
        })

    context = {
        'appliance_sections': appliance_sections
    }

    return render(request, 'pay/products/tv.html', context)

@login_required
def submit_rating(request):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            product_id = data.get("product_id")
            rating = data.get("rating")

            if not rating:
                return JsonResponse({"success": False, "error": "Rating is required"})

            rating = int(rating)
            if rating < 1 or rating > 5:
                return JsonResponse({"success": False, "error": "Invalid rating value"})

            user_id = request.user.id
            username = request.user.username

            # Save the rating to MongoDB
            save_rating(product_id, rating, user_id, username)

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"})



# Saving Activity Logs to MongoDB
@csrf_exempt
def log_activity_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = request.user.id if request.user.is_authenticated else None
        username = request.user.username if request.user.is_authenticated else "anonymous"
        action = data.get("action")
        product_id = data.get("product_id")
        page_url = data.get("page_url")

        log_activity(user_id, username, action, product_id, page_url)
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid method"}, status=405)



@login_required
def process_payment(request):
    user = request.user

    try:
        cart = Cart.objects.get(customer_id=user)
        cart_items = cart.items.all()

        # Serialize cart items
        cart_data = []
        total = 0
        for item in cart_items:
            product = item.product_id
            item_total = item.product_id.price * item.quantity
            total += item_total

            # Decrease the product stock
            if product.stock >= item.quantity:
                product.stock -= item.quantity
                product.save()
            else:
                return JsonResponse({'success': False, 'error': f'Not enough stock for {product.name}'})

            cart_data.append({
                'product_id': item.product_id.product_id,
                'product_name': item.product_id.name,
                'price': float(item.product_id.price),
                'quantity': item.quantity,
                'total': float(item_total),
            })

        # Create Transaction record
        transaction = Transaction.objects.create(
            user=user,
            cart_snapshot=cart_data,
            reference=str(uuid.uuid4())[:12].replace('-', ''),
            total_amount=total,
            status='success'
        )

        # Clear the cart after purchase
        cart_items.delete()

        return redirect('payment_success', transaction_id=transaction.transaction_id)

    except Cart.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cart not found'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def payment_success(request, transaction_id):
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
    return render(request, 'pay/customer/payment_success.html', {'transaction': transaction})


    

@login_required
def cart_history(request):
    user = request.user

    # Paid Carts (transactions)
    paid_transactions = Transaction.objects.filter(user=user, status='success').order_by('-created_at')

    # Pending Cart (current cart with items, unpaid)
    try:
        pending_cart = Cart.objects.get(customer_id=user)
        pending_items = pending_cart.items.all()
        pending_cart_data = []
        total = 0

        for item in pending_items:
            item_total = item.product_id.price * item.quantity
            total += item_total
            pending_cart_data.append({
                'product_id': item.product_id.product_id,
                'product_name': item.product_id.name,
                'price': float(item.product_id.price),
                'quantity': item.quantity,
                'total': float(item_total),
            })
    except Cart.DoesNotExist:
        pending_cart_data = []
        total = 0

    context = {
        'transactions': paid_transactions,
        'pending_cart_data': pending_cart_data,
        'pending_total': total,
    }

    return render(request, 'pay/customer/cart_history.html', context)




def all_transactions_view(request):
    transactions = Transaction.objects.all().order_by('-created_at')
    return render(request, 'pay/managers/all_transactions.html', {'transactions': transactions})




User = get_user_model()

def sales_report_view(request):
    transactions = Transaction.objects.filter(status='success')

    # Revenue & volume
    total_revenue = transactions.aggregate(total=Sum('total_amount'))['total'] or 0
    total_transactions = transactions.count()
    avg_transaction_value = transactions.aggregate(avg=Avg('total_amount'))['avg'] or 0

    # Revenue by Day (convert QuerySet to list of dicts)
    revenue_by_day = (
        Transaction.objects.filter(status="success")
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("total_amount"))
        .order_by("day")
    )

    # Convert to list of dicts (JSON serializable)
    revenue_by_day = list(revenue_by_day)

    # Step 1: Build a dictionary of product sales
    product_sales_dict = {}

    for txn in Transaction.objects.filter(status="success"):
        for item in txn.cart_snapshot:
            name = item["product_name"]
            quantity = item["quantity"]
            price = item["price"]
            if name not in product_sales_dict:
                product_sales_dict[name] = {"quantity": 0, "revenue": 0}
            product_sales_dict[name]["quantity"] += quantity
            product_sales_dict[name]["revenue"] += quantity * float(price)

    # Step 2: Convert to a list to be passed to the template (JSON serializable)
    product_sales = [{"product": name, **data} for name, data in product_sales_dict.items()]


    # Customer insights
    unique_customers = transactions.values('user').distinct().count()
    customer_spending = (
        transactions.values('user')
        .annotate(spent=Sum('total_amount'))
        .order_by('-spent')
    )
    top_customers = customer_spending[:5]

    context = {
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'avg_transaction_value': avg_transaction_value,
        'revenue_by_day': revenue_by_day,
        'unique_customers': unique_customers,
        'top_customers': top_customers,
        "revenue_by_day": revenue_by_day,
        "product_sales": product_sales,
    }

    return render(request, 'pay/managers/sales_report.html', context)




def log_user_activity(request):
    if request.method == "POST":
        data = request.POST
        action = data.get('action')
        product_id = data.get('product_id', None)
        page_url = data.get('page_url', None)

        # Save activity
        log_activity(
            user_id=None,  # Anonymous user
            username="Guest",
            action=action,
            product_id=product_id,
            page_url=page_url
        )
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




def guest_orders_page(request):
    return render(request, 'pay/guest_customer/orders.html')



def make_payment(request):
    # Render the make_payment page
    return render(request, 'pay/guest_customer/make_payment.html')



def process_payment(request):
    user = request.user

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        try:
            cart = Cart.objects.get(customer_id=user)
            cart_items = cart.items.all()

            if not cart_items.exists():
                # No items to pay for
                return redirect('cart_history')

            # Prepare cart snapshot
            cart_snapshot = []
            total = 0
            for item in cart_items:
                item_total = item.product_id.price * item.quantity
                cart_snapshot.append({
                    'product_name': item.product_id.name,
                    'price': float(item.product_id.price),
                    'quantity': item.quantity,
                    'total': float(item_total),
                })
                total += item_total

            # Create the transaction
            transaction = Transaction.objects.create(
                user=user,
                cart_snapshot=cart_snapshot,
                total_amount=total,
                status='success',  # assuming payment is successful here
                payment_method=payment_method,
                created_at=timezone.now()
            )

            # After successful payment, delete the cart
            cart.delete()

            # Redirect to success page
            return redirect('guest_transaction_success', reference=transaction.reference)

        except Cart.DoesNotExist:
            # Cart not found
            return redirect('cart_history')

    return redirect('make_payment')  # fallback if GET request




def guest_transaction_success(request, reference):
    # Get the transaction based on the reference ID
    transaction = get_object_or_404(Transaction, reference=reference)
    
    return render(request, 'pay/guest_customer/transaction_success.html', {'transaction': transaction})




@login_required
def delete_cart_item_again(request, product_id):
    user = request.user
    try:
        cart = Cart.objects.get(customer_id=user)
        item = cart.items.get(product_id__product_id=product_id)
        
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        pass

    return redirect('cart_history')
