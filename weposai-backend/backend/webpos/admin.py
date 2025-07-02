from django.contrib import admin
from .models import User, Store, Category, Product, Customer, Order, Sale, SaleItem, MarketTill, Transaction, Payment, InventoryAlert, Receipt

# Register your models here
admin.site.register(User)
admin.site.register(Store)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(MarketTill)
admin.site.register(Transaction)
admin.site.register(Payment)
admin.site.register(InventoryAlert)
admin.site.register(Receipt)
