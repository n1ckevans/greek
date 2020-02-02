from django.contrib import admin
from .models import Product, OrderItem, Order, Category, User, PromoCode, ShippingAddress
# Register your models here.


admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(User)
admin.site.register(PromoCode)
admin.site.register(ShippingAddress)