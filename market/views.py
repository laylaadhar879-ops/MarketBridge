from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.db.models import Sum
from .models import Shop, Product, Order, Payment
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
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

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
    products = []
    error_message = None

    try:
        response = requests.get('https://fakestoreapi.com/products', timeout=10)
        products = response.json()
    except requests.RequestException:
        error_message = 'Could not load external products right now. Please try again.'

    return render(request, 'products/external_products.html', {
        'products': products,
        'error_message': error_message,
    })
