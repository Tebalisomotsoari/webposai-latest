from django.contrib.auth.models import AbstractUser, Group, Permission # type: ignore
from django.db import models # type: ignore


# ----------------------------
# 1. User & Roles
# ----------------------------

class User(AbstractUser):
    ROLE_CHOICES = (
        ('cashier', 'Cashier'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')

    groups = models.ManyToManyField(
        Group,
        related_name='webpos_users',  # Unique related_name to avoid clashes
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='webpos_users',  # Unique related_name to avoid clashes
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username


# ----------------------------
# 2. Store (Physical or Online)
# ----------------------------

class Store(models.Model):
    STORE_TYPE = (
        ('physical', 'Physical'),
        ('online', 'Online'),
    )
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, null=True)
    store_type = models.CharField(max_length=20, choices=STORE_TYPE, default='physical')

    def __str__(self):
        return f"{self.name} ({self.store_type})"

# ----------------------------
# 3. Product Categories
# ----------------------------

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# ----------------------------
# 4. Products
# ----------------------------

class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=30, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    alert_threshold = models.PositiveIntegerField(default=5)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.sku})"

# ----------------------------
# 5. Customers
# ----------------------------

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# ----------------------------
# 6. Orders
# ----------------------------

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"

# ----------------------------
# 7. Sale and Sale Items
# ----------------------------

class Sale(models.Model):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    cashier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, default='cash')  # simplified for AIWebPOS

    def __str__(self):
        return f"Sale #{self.id} - {self.timestamp.date()}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# ----------------------------
# 8. Market Till (Cash register state per store)
# ----------------------------

class MarketTill(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    opening_balance = models.DecimalField(max_digits=10, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(blank=True, null=True)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return f"Till for {self.store.name} ({'Open' if self.is_open else 'Closed'})"

# ----------------------------
# 9. Transactions
# ----------------------------

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('payment', 'Payment'),
        ('refund', 'Refund'),
    )
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} for Sale #{self.sale.id}"

# ----------------------------
# 10. Payments
# ----------------------------

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('mobile', 'Mobile Money'),
        ('bank', 'Bank Transfer'),
    )
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.method.capitalize()} payment of ${self.transaction.amount}"

# ----------------------------
# 11. Inventory Alerts
# ----------------------------

class InventoryAlert(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert: {self.product.name} below threshold"

# ----------------------------
# 12. Receipt PDF Record
# ----------------------------

class Receipt(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='receipt')
    pdf_file = models.FileField(upload_to='receipts/')
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt for Sale #{self.sale.id}"
