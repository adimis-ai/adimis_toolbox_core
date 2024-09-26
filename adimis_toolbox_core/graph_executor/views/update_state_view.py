from typing import Any
from drf_yasg import openapi
from rest_framework import status
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..services import CompiledGraphService
from ...core import RunnableConfig
from rest_framework import serializers
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class UpdateStateRequestSerializer(serializers.Serializer):
    config = serializers.JSONField(required=True)
    values = serializers.JSONField(required=True)


class UpdateStateView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update the state of a compiled graph.",
        request_body=UpdateStateRequestSerializer,
        responses={
            200: openapi.Response(
                description="Updated configuration",
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
    def put(self, request: Request, graph_name: str) -> Response:
        try:
            config = RunnableConfig(**request.query_params)
            values = request.data
            updated_config = async_to_sync(self.service.updated_state)(
                graph_name, config, values
            )
            return Response(updated_config, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
