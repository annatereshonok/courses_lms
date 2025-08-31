from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
import stripe
import os

from .models import Course, Lesson, Subscription
from users.models import Payment
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    LessonSerializer,
    SubscriptionSerializer,
)
from .permissions import ModeratorPermission, OwnerPermission, is_moderator
from .pagination import LMSPagination
from .services.stripe_service import create_checkout_session


class CourseViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Course.objects.all()
    pagination_class = LMSPagination

    def get_permissions(self):
        if self.request.user.is_staff:
            self.permission_classes = [IsAuthenticated]
        elif self.action == "create":
            self.permission_classes = [~ModeratorPermission, IsAuthenticated]
        elif self.action in ("update", "partial_update", "retrieve"):
            self.permission_classes = [
                IsAuthenticated,
                OwnerPermission | ModeratorPermission,
            ]
        else:
            self.permission_classes = [IsAuthenticated, OwnerPermission]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        return (
            CourseDetailSerializer
            if self.action in ("retrieve",)
            else CourseListSerializer
        )

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        return qs if (is_moderator(user) or user.is_staff) else qs.filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        course = get_object_or_404(Course.objects.all(), pk=pk)
        sub, created = Subscription.objects.get_or_create(
            user=request.user, course=course
        )
        serializer = SubscriptionSerializer(sub)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        course = get_object_or_404(Course.objects.all(), pk=pk)
        deleted, _ = Subscription.objects.filter(
            user=request.user, course=course
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"detail": "Подписки не было."}, status=status.HTTP_404_NOT_FOUND
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="my/subscriptions",
        permission_classes=[IsAuthenticated],
    )
    def my_subscriptions(self, request):
        subs = Subscription.objects.filter(user=request.user).select_related(
            "user", "course"
        )
        ser = SubscriptionSerializer(subs, many=True, context={"request": request})
        return Response(ser.data)

    @action(
        methods=["post"],
        detail=True,
        url_path="buy",
        permission_classes=[IsAuthenticated],
    )
    def buy(self, request, pk=None):
        user = request.user
        course = get_object_or_404(Course.objects.all(), pk=pk)

        payment_stripe = create_checkout_session(
            course_name=course.name,
            course_id=course.id,
            user_email=getattr(user, "email", None),
            user_id=user.id,
            amount_cents=int(course.amount * 100),
        )

        Payment.objects.create(
            user=user,
            course=course,
            amount=course.amount,
            method="stripe",
            status="pending",
            stripe_session_id=payment_stripe.session_id,
        )

        return Response(
            {
                "checkout_url": payment_stripe.url,
                "session_id": payment_stripe.session_id,
            },
            status=200,
        )


class LessonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LessonSerializer
    pagination_class = LMSPagination

    def get_queryset(self):
        qs = Lesson.objects.select_related("owner", "course", "course__owner")
        user = self.request.user
        return qs if (is_moderator(user) or user.is_staff) else qs.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [
        IsAuthenticated,
        OwnerPermission | ModeratorPermission | IsAdminUser,
    ]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ~ModeratorPermission]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [
        IsAuthenticated,
        OwnerPermission | ModeratorPermission | IsAdminUser,
    ]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_update(self, serializer):
        u = self.request.user
        new_course = serializer.validated_data.get("course")
        if (
            new_course
            and not (u.is_staff or is_moderator(u))
            and new_course.owner_id != u.id
        ):
            raise PermissionDenied("Нельзя привязать урок к чужому курсу.")
        serializer.save()


class LessonDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, OwnerPermission | IsAdminUser]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer
