from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import VideoURLValidator
from users.serializers import CustomUserSerializer, CourseMiniSerializer


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ["id", "name", "description", "preview", "video_url",  "course", "owner"]
        read_only_fields = ["id", "owner"]
        validators = [VideoURLValidator(field="video_url")]


class CourseListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        lessons_count = obj.lessons.count()
        return lessons_count

    def get_user_subscribed(self, obj):
        user = self.context["request"].user
        return Subscription.objects.filter(user=user, course=obj.course).exists()

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons_count"]


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons"]


class SubscriptionSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    course = CourseMiniSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "user", "course"]
