from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "name", "description", "preview", "video_url",  "course", "owner"]
        read_only_fields = ["id", "owner"]


class CourseListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    def get_lessons_count(self, obj):
        lessons_count = obj.lessons.count()
        return lessons_count

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons_count"]


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "preview", "description", "lessons"]
