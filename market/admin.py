from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Shop, Product, Order, Payment

# Register your models here.

"""
Admin Configuration
- Configures the Django admin interface for managing users, shops, products, orders, and payments.
- Customizes the display and search options for each model in the admin interface.

"""

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role Information", {"fields": ("role",)}),
    )

    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("username",)


"""
Product Inline (Inside Shop)
- Allows products to be edited inline within the shop admin interface.
- Displays product name, price, stock, and creation date in the inline form.

"""
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ("name", "price", "stock", "created_at")
    readonly_fields = ("created_at",)


"""
Shop Admin
- Configures the admin interface for managing shops.
- Displays shop name, owner, and creation date in the list view.
- Allows searching by shop name and owner username.
- Filters shops by creation date.
- Includes an inline form for managing products within each shop.

"""

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("shop_name", "owner", "created_at")
    search_fields = ("shop_name", "owner__username")
    list_filter = ("created_at",)
    inlines = [ProductInline]


"""
Product Admin
- Configures the admin interface for managing products.
- Displays product name, associated shop, price, stock, and creation date in the list view.
- Allows searching by product name and shop name.
- Filters products by associated shop and creation date.
- Orders products by creation date in descending order.

"""

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "shop", "price", "stock", "created_at")
    search_fields = ("name", "shop__shop_name")
    list_filter = ("shop", "created_at")
    ordering = ("-created_at",)

"""
Payment Inline (Inside Order)
- Allows payments to be edited inline within the order admin interface.
- Displays payment amount, method, status, and date in the inline form.

"""
class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    readonly_fields = ("payment_date",)


"""
Order Admin
- Configures the admin interface for managing orders.
- Displays order ID, associated user, status, total amount, payment status, and order date in the list view.
- Allows searching by associated user's username.
- Filters orders by status, payment status, and order date.
- Orders orders by order date in descending order.
- Includes an inline form for managing payments associated with each order.

"""

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "payment_status", "order_date")
    search_fields = ("user__username",)
    list_filter = ("status", "payment_status", "order_date")
    ordering = ("-order_date",)
    inlines = [PaymentInline]


"""
Payment Admin
- Configures the admin interface for managing payments.
- Displays associated order, payment amount, method, status, and payment date in the list view.
- Allows searching by associated order ID.
- Filters payments by method, status, and payment date.
- Orders payments by payment date in descending order.

"""

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "payment_method", "payment_status", "payment_date")
    search_fields = ("order__id",)
    list_filter = ("payment_method", "payment_status", "payment_date")
    ordering = ("-payment_date",)