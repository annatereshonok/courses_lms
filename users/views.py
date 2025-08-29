from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes
from django.contrib.auth import get_user_model

from .models import Payment
from .serializers import PaymentListSerializer, EmailTokenObtainPairSerializer, RegisterSerializer

User = get_user_model()


@permission_classes([IsAuthenticated])
class PaymentListAPIView(generics.ListAPIView):
    queryset = Payment.objects.select_related("user", "course", "lesson")
    serializer_class = PaymentListSerializer

    filter_backends = [filters.DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        "method": ["exact"],
        "course__name": ["icontains"],
        "lesson__name": ["icontains"]
    }
    ordering_fields = ["paid_at"]
    ordering = ["-paid_at"]


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@permission_classes([AllowAny])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
