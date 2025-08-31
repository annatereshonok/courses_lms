from django.urls import path
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter

from lms.views import (
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonCreateAPIView,
    LessonUpdateAPIView,
    LessonDestroyAPIView,
    CourseViewSet,
)

app_name = "lms"

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

urlpatterns = [
    path("lessons/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lessons/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-retrieve"),
    path("lessons/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path(
        "lessons/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"
    ),
    path(
        "lessons/delete/<int:pk>/", LessonDestroyAPIView.as_view(), name="lesson-delete"
    ),
    path("payment/success/", lambda r: HttpResponse("OK"), name="payment-success"),
    path("payment/cancel/", lambda r: HttpResponse("Canceled"), name="payment-cancel"),
] + router.urls
