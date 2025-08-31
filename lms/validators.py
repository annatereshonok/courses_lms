from rest_framework import serializers
from urllib.parse import urlparse


class VideoURLValidator:
    def __init__(self, field: str):
        self.field = field

    def __call__(self, attrs):
        url = attrs.get(self.field)
        netloc = urlparse(url).netloc.lower()
        if not netloc:
            return attrs
        if "youtube.com" not in netloc:
            raise serializers.ValidationError(
                {self.field: "Ссылка должна быть с YouTube."}
            )
        return attrs
