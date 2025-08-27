from django.urls import path

from .views import PaymentListAPIView

app_name = "users"

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
]
