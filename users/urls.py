from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import PaymentListAPIView, EmailTokenObtainPairView, RegisterView

app_name = "users"

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("auth/register/", RegisterView.as_view(), name='register'),
    path("auth/token/", EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name='token_refresh'),
    path("auth/token/verify/", TokenVerifyView.as_view(), name='token_verify'),
]
