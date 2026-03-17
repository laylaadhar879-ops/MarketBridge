from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.db.models import Sum
from .models import Shop, Product, Order, Payment, CartItem
from .forms import SignUpForm
from decimal import Decimal
import requests


# -------------------------
# Shop Views
# -------------------------

def shop_list(request):
    shops = Shop.objects.all()
    return render(request, 'shops/shop_list.html', {'shops': shops})


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


def shop_detail(request, shop_id):
    shop = get_object_or_404(Shop, id=shop_id)
    products = shop.products.all()
    return render(request, 'shops/shop_detail.html', {
        'shop': shop,
        'products': products
    })


# -------------------------
# Product Views
# -------------------------

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})


# -------------------------
# Create Order
# -------------------------

@login_required
def create_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.stock <= 0:
        return render(request, 'orders/error.html', {
            'message': 'Product out of stock.'
        })

    # Create order
    order = Order.objects.create(
        user=request.user,
        total_amount=product.price,
        status='pending',
        payment_status='pending'
    )

    # Reduce stock
    product.stock -= 1
    product.save()

    return redirect('order_detail', order_id=order.id)


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# -------------------------
# User Orders
# -------------------------

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/user_orders.html', {'orders': orders})


# -------------------------
# Payment View
# -------------------------

@login_required
def create_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.payment_status == 'paid':
        return render(request, 'orders/error.html', {
            'message': 'Order already paid.'
        })

    payment = Payment.objects.create(
        order=order,
        amount=order.total_amount,
        payment_method='stripe',
        payment_status='completed'
    )

    order.payment_status = 'paid'
    order.status = 'completed'
    order.save()

    return redirect('order_detail', order_id=order.id)


# -------------------------
# Owner Dashboard
# -------------------------

@login_required
def owner_dashboard(request):
    if request.user.role != 'owner':
        return render(request, 'orders/error.html', {
            'message': 'Access denied.'
        })

    shop = get_object_or_404(Shop, owner=request.user)
    products = shop.products.all()
    total_products = products.count()

    total_sales = Payment.objects.filter(
        order__user__isnull=False,
        order__status='completed'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

    return render(request, 'dashboard/owner_dashboard.html', {
        'shop': shop,
        'products': products,
        'total_products': total_products,
        'total_sales': total_sales,
    })


def external_products(request):
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    sort_by = request.GET.get('sort', '').strip()
    products = []
    categories = []
    error_message = None

    try:
        response = requests.get('https://fakestoreapi.com/products', timeout=10)
        products = response.json()

        # Build unique category list before filtering
        categories = sorted(set(p.get('category', '') for p in products))

        if search_query:
            query = search_query.lower()
            products = [
                p for p in products
                if query in p.get('title', '').lower()
                or query in p.get('category', '').lower()
            ]

        if category_filter:
            products = [p for p in products if p.get('category', '') == category_filter]

        if min_price:
            try:
                products = [p for p in products if float(p.get('price', 0)) >= float(min_price)]
            except ValueError:
                pass

        if max_price:
            try:
                products = [p for p in products if float(p.get('price', 0)) <= float(max_price)]
            except ValueError:
                pass

        if sort_by == 'price_asc':
            products = sorted(products, key=lambda p: float(p.get('price', 0)))
        elif sort_by == 'price_desc':
            products = sorted(products, key=lambda p: float(p.get('price', 0)), reverse=True)
        elif sort_by == 'name_asc':
            products = sorted(products, key=lambda p: p.get('title', '').lower())

    except requests.RequestException:
        error_message = 'Could not load external products right now. Please try again.'

    return render(request, 'products/external_products.html', {
        'products': products,
        'error_message': error_message,
        'search_query': search_query,
        'categories': categories,
        'category_filter': category_filter,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })


@login_required
def basket(request):
    items = CartItem.objects.filter(user=request.user)
    cart_items = [{
        'id': item.product_id,
        'title': item.title,
        'price': item.price,
        'image': item.image,
        'quantity': item.quantity,
        'line_total': item.line_total(),
    } for item in items]
    subtotal = round(sum(c['line_total'] for c in cart_items), 2)
    return render(request, 'orders/basket.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
    })


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        pid = str(request.POST.get('product_id'))
        title = request.POST.get('title', '')
        price = request.POST.get('price', '0')
        image = request.POST.get('image', '')
        try:
            quantity = max(1, int(request.POST.get('quantity', 1)))
        except ValueError:
            quantity = 1

        item, created = CartItem.objects.get_or_create(
            user=request.user,
            product_id=pid,
            defaults={'title': title, 'price': price, 'image': image, 'quantity': quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()
    return redirect('basket')


@login_required
def remove_from_cart(request, product_id):
    CartItem.objects.filter(user=request.user, product_id=str(product_id)).delete()
    return redirect('basket')


@login_required
def update_cart(request, product_id):
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1
        if quantity <= 0:
            CartItem.objects.filter(user=request.user, product_id=str(product_id)).delete()
        else:
            CartItem.objects.filter(user=request.user, product_id=str(product_id)).update(quantity=quantity)
    return redirect('basket')
