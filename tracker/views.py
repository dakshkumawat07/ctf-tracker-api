from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Challenge, Event, Writeup
from .serializers import (
    ChallengeSerializer,
    EventSerializer,
    RegisterSerializer,
    WriteupSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer

    def get_queryset(self):
        return Event.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChallengeViewSet(viewsets.ModelViewSet):
    serializer_class = ChallengeSerializer

    def get_queryset(self):
        queryset = Challenge.objects.filter(
            event__owner=self.request.user
        ).select_related("event")

        event_id = self.request.query_params.get("event")
        if event_id and event_id.isdigit():
            queryset = queryset.filter(event_id=event_id)

        solved = self.request.query_params.get("solved")
        if solved in ("true", "false"):
            queryset = queryset.filter(solved=solved == "true")

        return queryset


class WriteupViewSet(viewsets.ModelViewSet):
    serializer_class = WriteupSerializer

    def get_queryset(self):
        queryset = Writeup.objects.filter(
            challenge__event__owner=self.request.user
        ).select_related("challenge")

        challenge_id = self.request.query_params.get("challenge")
        if challenge_id and challenge_id.isdigit():
            queryset = queryset.filter(challenge_id=challenge_id)

        return queryset


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({"status": "ok", "service": "ctf-tracker-api"})
