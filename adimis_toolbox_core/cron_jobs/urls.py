from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PeriodicTaskViewSet,
    IntervalScheduleViewSet,
    CrontabScheduleViewSet,
    SolarScheduleViewSet,
    ClockedScheduleViewSet,
)

router = DefaultRouter()
router.register(r"periodic-tasks", PeriodicTaskViewSet)
router.register(r"interval-schedules", IntervalScheduleViewSet)
router.register(r"crontab-schedules", CrontabScheduleViewSet)
router.register(r"solar-schedules", SolarScheduleViewSet)
router.register(r"clocked-schedules", ClockedScheduleViewSet)

urlpatterns = [
    path("cron-jobs/", include(router.urls)),
]
