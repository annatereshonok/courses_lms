from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import Payment
from lms.models import Course, Lesson

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "avatar", "phone", "city"]


class CourseMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "preview"]


class LessonMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name", "preview"]


class PaymentListSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    course = CourseMiniSerializer(read_only=True)
    lesson = LessonMiniSerializer(read_only=True)
    method_display = serializers.CharField(source="get_method_display", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id", "paid_at", "amount",
            "method", "method_display",
            "user", "course", "lesson",
        ]
