from rest_framework.routers import DefaultRouter

from .views import ChallengeViewSet, EventViewSet, WriteupViewSet

router = DefaultRouter()
router.register("events", EventViewSet, basename="event")
router.register("challenges", ChallengeViewSet, basename="challenge")
router.register("writeups", WriteupViewSet, basename="writeup")

urlpatterns = router.urls
