from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import permission_classes
from django.contrib.auth import get_user_model

from .models import Payment
from .serializers import (
    PaymentListSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .permissions import IsSelfUserOrAdmin

User = get_user_model()


@permission_classes([IsAuthenticated])
class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.select_related("user", "course", "lesson")
    serializer_class = PaymentListSerializer

    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "method": ["exact"],
        "course__name": ["icontains"],
        "lesson__name": ["icontains"],
    }
    ordering_fields = ["paid_at"]
    ordering = ["-paid_at"]


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSelfUserOrAdmin]


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSelfUserOrAdmin]


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsSelfUserOrAdmin]


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
