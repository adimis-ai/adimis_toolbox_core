from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from django_celery_beat.models import (
    PeriodicTask,
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
)

from .serializers import (
    PeriodicTaskSerializer,
    IntervalScheduleSerializer,
    CrontabScheduleSerializer,
    SolarScheduleSerializer,
    ClockedScheduleSerializer,
)

class PeriodicTaskViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing PeriodicTask instances.
    """
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def run_task(self, request, pk=None):
        task = self.get_object()
        task.apply_async()
        return Response({'status': 'task started'})


class IntervalScheduleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing IntervalSchedule instances.
    """
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSerializer
    permission_classes = [IsAuthenticated]


class CrontabScheduleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing CrontabSchedule instances.
    """
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSerializer
    permission_classes = [IsAuthenticated]


class SolarScheduleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing SolarSchedule instances.
    """
    queryset = SolarSchedule.objects.all()
    serializer_class = SolarScheduleSerializer
    permission_classes = [IsAuthenticated]


class ClockedScheduleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing ClockedSchedule instances.
    """
    queryset = ClockedSchedule.objects.all()
    serializer_class = ClockedScheduleSerializer
    permission_classes = [IsAuthenticated]
