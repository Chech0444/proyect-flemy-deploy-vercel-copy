from django.urls import path
from .views import (
    ProductListView,
    SimulatedPaymentView,
    SimulatedPurchaseView,
    WompiConfigView,
    WompiVerifyView,
    WompiPurchaseVerifyView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="product-list"),
    path("pay/simulate/", SimulatedPaymentView.as_view(), name="simulate-payment"),
    path("purchase/simulate/", SimulatedPurchaseView.as_view(), name="simulate-purchase"),
    path("wompi/config/", WompiConfigView.as_view(), name="wompi-config"),
    path("wompi/verify/", WompiVerifyView.as_view(), name="wompi-verify"),
    path("wompi/purchase-verify/", WompiPurchaseVerifyView.as_view(), name="wompi-purchase-verify"),
]
