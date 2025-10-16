from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    PaymentListAPIView,
    EmailTokenObtainPairView,
    UserCreateView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
    UserDestroyAPIView,
)

app_name = "users"

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("auth/register/", UserCreateView.as_view(), name="user-create"),
    path("auth/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path("users/update/<int:pk>/", UserUpdateAPIView.as_view(), name="user-update"),
    path("users/delete/<int:pk>/", UserDestroyAPIView.as_view(), name="user-delete"),
]
