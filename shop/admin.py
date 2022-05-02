from django.contrib import admin
from shop.models import User, Shop, Category, Order, OrderItem, Contact, \
    ConfirmEmailToken


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = [
        "date_joined", "is_staff", "groups", "user_permissions",
        "is_superuser", "last_login"
    ]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
