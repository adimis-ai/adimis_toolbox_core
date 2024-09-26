from typing import Any
from drf_yasg import openapi
from rest_framework import status
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..services import CompiledGraphService
from rest_framework import serializers
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class InvokeGraphRequestSerializer(serializers.Serializer):
    input = serializers.JSONField(required=True)
    config = serializers.JSONField(required=False)
    stream_mode = serializers.ListField(
        child=serializers.ChoiceField(choices=["values", "updates", "debug"]),
        required=False,
        allow_null=True,
        default=["debug"],
    )
    output_keys = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
    interrupt_before = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )
    interrupt_after = serializers.ListField(
        child=serializers.CharField(), required=False, allow_null=True
    )


class InvokeGraphView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Invoke the compiled graph.",
        request_body=InvokeGraphRequestSerializer,
        responses={
            200: openapi.Response(
                description="Result of graph invocation",
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
        try:
            input_data = request.data.get("input", {})
            config = request.data.get("config", None)
            result = async_to_sync(self.service.invoke)(graph_name, input_data, config)
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
