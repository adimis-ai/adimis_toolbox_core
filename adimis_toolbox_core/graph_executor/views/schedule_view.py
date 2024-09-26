from typing import Any
from drf_yasg import openapi
from rest_framework import status
from asgiref.sync import async_to_sync
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.request import Request
from ..services import CompiledGraphService
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class ScheduleGraphRequestSerializer(serializers.Serializer):
    pass


class ScheduleGraphView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Schedule the execution of compiled graph with prefined runtime config, inputs as a cron job.",
        request_body=ScheduleGraphRequestSerializer,
        responses={
            200: openapi.Response(
                description="Scheduled execution",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT),
            ),
            404: openapi.Response(
                description="Graph not found",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT),
            ),
            500: openapi.Response(
                description="An unexpected error occurred",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT),
            ),
        },
    )
    def post(self, request: Request, graph_name: str) -> Response:
        pass
