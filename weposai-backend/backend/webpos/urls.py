from django.urls import path, include # type: ignore
from rest_framework import routers # type: ignore
from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'sales', SaleViewSet)
router.register(r'saleitems', SaleItemViewSet)
router.register(r'markettills', MarketTillViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'inventoryalerts', InventoryAlertViewSet)
router.register(r'receipts', ReceiptViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
