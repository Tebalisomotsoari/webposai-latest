from rest_framework import serializers
from .models import (
    User, Store, Category, Product, Customer, Order,
    Sale, SaleItem, MarketTill, Transaction, Payment,
    InventoryAlert, Receipt
)


# ----------------------------
# 1. User Serializer
# ----------------------------

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_active']


# ----------------------------
# 2. Store Serializer
# ----------------------------

class StoreSerializer(serializers.ModelSerializer):
    manager = UserSerializer(read_only=True)

    class Meta:
        model = Store
        fields = ['id', 'name', 'location', 'store_type', 'manager']


# ----------------------------
# 3. Category Serializer
# ----------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


# ----------------------------
# 4. Product Serializer
# ----------------------------

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'price', 'discount',
            'quantity', 'alert_threshold', 'unit_type',
            'category', 'store'
        ]


# ----------------------------
# 5. Customer Serializer
# ----------------------------

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'created_at']


# ----------------------------
# 6. Order Serializer
# ----------------------------

class OrderSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'store', 'status',
            'created_at', 'updated_at', 'created_by'
        ]


# ----------------------------
# 7. Sale & Sale Item Serializer
# ----------------------------

class SaleItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'quantity', 'price_at_sale', 'subtotal']


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    cashier = UserSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Sale
        fields = [
            'id', 'order', 'timestamp', 'cashier',
            'store', 'customer', 'total', 'payment_method', 'items'
        ]


# ----------------------------
# 8. Market Till Serializer
# ----------------------------

class MarketTillSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)
    opened_by = UserSerializer(read_only=True)
    closed_by = UserSerializer(read_only=True)

    class Meta:
        model = MarketTill
        fields = [
            'id', 'store', 'opening_balance', 'closing_balance',
            'opened_at', 'closed_at', 'is_open',
            'opened_by', 'closed_by'
        ]


# ----------------------------
# 9. Transaction & Payment
# ----------------------------

class TransactionSerializer(serializers.ModelSerializer):
    sale = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'sale', 'transaction_type', 'amount', 'timestamp']


class PaymentSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'transaction', 'method', 'reference']


# ----------------------------
# 10. Inventory Alert
# ----------------------------

class InventoryAlertSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = InventoryAlert
        fields = ['id', 'product', 'created_at', 'resolved']


# ----------------------------
# 11. Receipt
# ----------------------------

class ReceiptSerializer(serializers.ModelSerializer):
    sale = SaleSerializer(read_only=True)

    class Meta:
        model = Receipt
        fields = ['id', 'sale', 'pdf_file', 'generated_at', 'pdf_generated']
