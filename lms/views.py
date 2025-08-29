from rest_framework import viewsets, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson
from .serializers import CourseListSerializer, CourseDetailSerializer, LessonSerializer
from .permissions import ModeratorPermission, OwnerPermission, is_moderator


class CourseViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    queryset = Course.objects.all()

    def get_serializer_class(self):
        return CourseDetailSerializer if self.action in ("retrieve",) else CourseListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs if is_moderator(self.request.user) else qs.filter(owner=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)


class LessonListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, ModeratorPermission, OwnerPermission]
    serializer_class = LessonSerializer

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
