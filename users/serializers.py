from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import Payment
from lms.models import Course, Lesson, Subscription

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "avatar", "phone", "city"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "avatar", "phone", "password", "password2")
        read_only_fields = ("id", )

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2", None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = ("id", "email", "avatar", "phone", "password")
        read_only_fields = ("id", )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user


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


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token
