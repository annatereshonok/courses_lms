from rest_framework import generics
from rest_framework.filters import OrderingFilter
from django_filters import rest_framework as filters

from .models import Payment
from .serializers import PaymentListSerializer


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

