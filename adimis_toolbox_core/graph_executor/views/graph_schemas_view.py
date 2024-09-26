from typing import Any
from drf_yasg import openapi
from rest_framework import status
from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..services import CompiledGraphService
from django.conf import settings
from rest_framework.permissions import IsAuthenticated


class GraphSchemasView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the graph schemas for a compiled graph.",
        manual_parameters=[
            openapi.Parameter(
                "graph_name",
                openapi.IN_PATH,
                description="Name of the graph",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Graph schema details",
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
    def get(self, request: Request, graph_name: str) -> Response:
        try:
            schema = async_to_sync(self.service.get_graph_schemas)(graph_name)
            return Response(schema, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
