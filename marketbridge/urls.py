"""
URL configuration for marketbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from market import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.shop_list, name='home'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shops/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/external/', views.external_products, name='external_products'),
    path('basket/', views.basket, name='basket'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:product_id>/', views.update_cart, name='update_cart'),
    path('orders/create/<int:product_id>/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.user_orders, name='user_orders'),
    path('payments/create/<int:order_id>/', views.create_payment, name='create_payment'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
]