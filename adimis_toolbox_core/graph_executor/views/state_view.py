from typing import Any
from drf_yasg import openapi
from rest_framework import status
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..services import CompiledGraphService
from ...core import RunnableConfig, serialize_state_snapshot
from rest_framework import serializers
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class GetStateRequestSerializer(serializers.Serializer):
    graph_name = serializers.CharField(required=True)
    config = serializers.JSONField(required=False)


class StateView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the current state for a compiled graph.",
        request_body=GetStateRequestSerializer,
        responses={
            200: openapi.Response(
                description="Current state snapshot",
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
    def post(self, request: Request) -> Response:
        try:
            serializer = GetStateRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            graph_name = serializer.validated_data["graph_name"]
            config = RunnableConfig(**serializer.validated_data.get("config", {}))
            state = async_to_sync(self.service.get_state)(graph_name, config)
            return Response(serialize_state_snapshot(state), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
