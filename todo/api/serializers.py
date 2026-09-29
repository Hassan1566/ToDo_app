from rest_framework import serializers
from .models import LocalTask


class LocalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocalTask
        fields = [
            "id",
            "user",
            "title",
            "notes",
            "is_completed",
            "google_task_id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "google_task_id",
            "created_at",
            "updated_at",
        ]
