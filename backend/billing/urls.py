from django.urls import path
from .views import SimulatedPaymentView

urlpatterns = [
    path("pay/simulate/", SimulatedPaymentView.as_view(), name="simulate-payment"),
]
