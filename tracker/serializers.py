from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Challenge, Event, Writeup


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name", "platform", "event_date", "url", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class ChallengeSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source="event.name", read_only=True)

    class Meta:
        model = Challenge
        fields = [
            "id",
            "event",
            "event_name",
            "title",
            "category",
            "points",
            "solved",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_event(self, value):
        if value.owner != self.context["request"].user:
            raise serializers.ValidationError(
                "You can only add challenges to your own events."
            )
        return value


class WriteupSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source="challenge.title", read_only=True)

    class Meta:
        model = Writeup
        fields = [
            "id",
            "challenge",
            "challenge_title",
            "title",
            "content",
            "tools_used",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Content cannot be empty.")
        return value

    def validate_challenge(self, value):
        if value.event.owner != self.context["request"].user:
            raise serializers.ValidationError(
                "You can only add writeups to your own challenges."
            )
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
