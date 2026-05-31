from django.urls import path
from .views import SimulatedPaymentView, WompiConfigView, WompiVerifyView

urlpatterns = [
    path("pay/simulate/", SimulatedPaymentView.as_view(), name="simulate-payment"),
    path("wompi/config/", WompiConfigView.as_view(), name="wompi-config"),
    path("wompi/verify/", WompiVerifyView.as_view(), name="wompi-verify"),
]
