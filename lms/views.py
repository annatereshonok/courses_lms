from rest_framework import viewsets, generics
from django.db.models import Count, Prefetch
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from .models import Course, Lesson
from .serializers import CourseListSerializer, CourseDetailSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    queryset = Course.objects.all()

    def get_serializer_class(self):
        return CourseDetailSerializer if self.action in ("retrieve",) else CourseListSerializer

    def get_queryset(self):
        qs = Course.objects.all()
        if self.action in ("list",):
            qs = qs.annotate(lessons_count=Count("lessons"))
        if self.action in ("retrieve",):
            qs = qs.prefetch_related(
                Prefetch("lessons", queryset=Lesson.objects.order_by("id"))
            )
        return qs


class LessonListAPIView(generics.ListAPIView):
    queryset = Lesson.objects.select_related("course")
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.select_related("course")
    serializer_class = LessonSerializer


class LessonCreateAPIView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
