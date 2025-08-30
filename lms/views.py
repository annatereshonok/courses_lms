from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Course, Lesson, Subscription
from .serializers import CourseListSerializer, CourseDetailSerializer, LessonSerializer, SubscriptionSerializer
from .permissions import ModeratorPermission, OwnerPermission, is_moderator
from .pagination import LMSPagination


class CourseViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Course.objects.all()
    pagination_class = LMSPagination

    def get_serializer_class(self):
        return CourseDetailSerializer if self.action in ("retrieve",) else CourseListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs if is_moderator(self.request.user) else qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        course = get_object_or_404(Course.objects.all(), pk=pk)
        sub, created = Subscription.objects.get_or_create(user=request.user, course=course)
        serializer = SubscriptionSerializer(sub)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk=None):
        course = get_object_or_404(Course.objects.all(), pk=pk)
        deleted, _ = Subscription.objects.filter(user=request.user, course=course).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Подписки не было."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["get"], url_path="my/subscriptions", permission_classes=[IsAuthenticated])
    def my_subscriptions(self, request):
        subs = (Subscription.objects
                .filter(user=request.user)
                .select_related("user", "course"))
        ser = SubscriptionSerializer(subs, many=True, context={"request": request})
        return Response(ser.data)


class LessonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    serializer_class = LessonSerializer
    pagination_class = LMSPagination

    def get_queryset(self):
        qs = Lesson.objects.select_related("course", "course__owner")
        return qs if is_moderator(self.request.user) else qs.filter(course__owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if not is_moderator(self.request.user) and course.owner != self.request.user:
            raise PermissionDenied("Нельзя создавать урок в чужом курсе.")
        serializer.save()


class LessonUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def perform_update(self, serializer):
        new_course = serializer.validated_data.get("course")
        if new_course and not is_moderator(self.request.user) and new_course.owner != self.request.user:
            raise PermissionDenied("Нельзя привязать урок к чужому курсу.")
        serializer.save()


class LessonDestroyAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Lesson.objects.select_related("course", "course__owner")
    serializer_class = LessonSerializer
