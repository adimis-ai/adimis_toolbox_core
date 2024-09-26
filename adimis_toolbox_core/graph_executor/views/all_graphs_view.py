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


class AllGraphsView(APIView):
    def __init__(self, **kwargs: Any) -> None:
        self.service = CompiledGraphService()
        super().__init__(**kwargs)

    if settings.IS_GRAPH_API_PUBLIC:
        permission_classes = []
    else:
        permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the schemas for all compiled graphs.",
        responses={
            200: openapi.Response(
                description="List of all graph schemas",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_OBJECT),
                        ),
                    },
                ),
            ),
            500: openapi.Response(
                description="An unexpected error occurred",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT),
            ),
        },
    )
    def get(self, request: Request) -> Response:
        try:
            schemas = async_to_sync(self.service.get_all_graph_schemas)()
            response_data = {
                "count": len(schemas),
                "data": schemas,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
