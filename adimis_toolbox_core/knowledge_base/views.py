import json
import uuid
from drf_yasg import openapi
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from .services import CollectionService, DocumentService
from .serializers import (
    WorkspaceCollectionSerializer,
    WorkspaceCollectionDocumentSerializer,
)


@method_decorator(csrf_exempt, name="dispatch")
class CollectionListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Name of the collection"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the collection",
                ),
            },
            required=["name"],
        ),
        responses={
            201: openapi.Response("Collection created successfully"),
            400: "Bad request",
        },
    )
    def post(self, request):
        try:
            data = json.loads(request.body)
            name = data.get("name")
            description = data.get("description")
            user = request.user

            collection = CollectionService.create_collection(name, description, user)
            serializer = WorkspaceCollectionSerializer(collection)
            return JsonResponse(serializer.data, status=201)

        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Retrieve all collections with pagination",
        responses={
            200: openapi.Response(
                "Collections retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: "Bad request",
        },
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Number of collections to return",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=100,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Number of collections to skip",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=0,
            ),
        ],
    )
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", 100))
            offset = int(request.GET.get("offset", 0))

            collections_data = CollectionService.get_all_collections(
                limit=limit, offset=offset
            )

            response_data = {
                "count": collections_data["count"],
                "response": WorkspaceCollectionSerializer(
                    collections_data["response"], many=True
                ).data,
            }
            return JsonResponse(response_data)

        except ValueError:
            return HttpResponseBadRequest("Invalid limit or offset value.")
        except Exception as e:
            return HttpResponseBadRequest(str(e))


@method_decorator(csrf_exempt, name="dispatch")
class CollectionDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a collection by name",
        responses={
            200: openapi.Response("Collection retrieved successfully"),
            404: "Collection not found",
        },
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Name of the collection",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
    )
    def get(self, request):
        try:
            collection_name = request.GET.get("collection_name")
            collection = CollectionService.get_collection_by_name(collection_name)
            serializer = WorkspaceCollectionSerializer(collection)
            return JsonResponse(serializer.data)

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Collection not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Update a collection by name",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New name of the collection"
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="New description of the collection",
                ),
            },
            required=["name"],
        ),
        responses={
            200: openapi.Response("Collection updated successfully"),
            404: "Collection not found",
            400: "Bad request",
        },
    )
    def put(self, request):
        try:
            data = json.loads(request.body)
            new_name = data.get("name")
            description = data.get("description")
            user = request.user

            collection_name = request.GET.get("collection_name")
            collection = CollectionService.get_collection_by_name(collection_name)
            updated_collection = CollectionService.update_collection(
                collection.id, new_name, description, user
            )
            serializer = WorkspaceCollectionSerializer(updated_collection)
            return JsonResponse(serializer.data)

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Collection not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Delete a collection by name",
        responses={
            204: openapi.Response("Collection deleted successfully"),
            404: "Collection not found",
            400: "Bad request",
        },
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Name of the collection",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
    )
    def delete(self, request):
        try:
            collection_name = request.GET.get("collection_name")
            collection = CollectionService.get_collection_by_name(collection_name)
            CollectionService.delete_collection(collection.id)
            return JsonResponse(
                {"message": "Collection deleted successfully"}, status=204
            )

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Collection not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))


@method_decorator(csrf_exempt, name="dispatch")
class ResetCollectionView(APIView):
    @swagger_auto_schema(
        operation_description="Reset a collection by deleting all its documents",
        responses={
            204: openapi.Response("Collection reset successfully"),
            404: "Collection not found",
            400: "Bad request",
        },
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Name of the collection",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
    )
    def post(self, request):
        try:

            collection_name = request.GET.get("collection_name")
            collection = CollectionService.get_collection_by_name(collection_name)
            CollectionService.reset_collection(collection.id)
            return JsonResponse(
                {"message": "Collection reset successfully"}, status=204
            )

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Collection not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))


@method_decorator(csrf_exempt, name="dispatch")
class DocumentListCreateView(APIView):
    @swagger_auto_schema(
        operation_description="Create a new document in a collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Title of the document"
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Content of the document"
                ),
                "metadata": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="Metadata of the document"
                ),
            },
            required=["title", "content"],
        ),
        responses={
            201: openapi.Response("Document created successfully"),
            400: "Bad request",
        },
    )
    def post(self, request, collection_name):
        try:
            data = json.loads(request.body)
            title = data.get("title")
            content = data.get("content")
            metadata = data.get("metadata", {})
            user = request.user

            document_service = DocumentService.from_default_settings(collection_name)
            document = document_service.create_document(title, content, metadata, user)
            serializer = WorkspaceCollectionDocumentSerializer(document)
            return JsonResponse(serializer.data, status=201)

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Collection not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Retrieve all documents in a collection",
        responses={
            200: openapi.Response(
                "Documents retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "page": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "page_size": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                                    "content": openapi.Schema(type=openapi.TYPE_STRING),
                                    "metadata": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING, format="date-time"
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING, format="date-time"
                                    ),
                                    "created_by": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "updated_by": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: "Bad request",
        },
        manual_parameters=[
            openapi.Parameter(
                "collection_name",
                openapi.IN_QUERY,
                description="Name of the collection",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Number of documents to return",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=100,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Number of documents to skip",
                type=openapi.TYPE_INTEGER,
                required=False,
                default=0,
            ),
        ],
    )
    def get(self, request, collection_name):
        try:
            limit = int(request.GET.get("limit", 100))
            offset = int(request.GET.get("offset", 0))

            document_service = DocumentService.from_default_settings(collection_name)
            documents_data = document_service.get_all_documents(
                limit=limit, offset=offset
            )

            response_data = {
                "count": documents_data["count"],
                "response": WorkspaceCollectionDocumentSerializer(
                    documents_data["response"], many=True
                ).data,
            }

            return JsonResponse(response_data)

        except Exception as e:
            return HttpResponseBadRequest(str(e))


@method_decorator(csrf_exempt, name="dispatch")
class DocumentDetailView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a document by ID",
        responses={
            200: openapi.Response("Document retrieved successfully"),
            404: "Document not found",
        },
        manual_parameters=[],
    )
    def get(self, request, collection_name, document_id):
        try:
            document_service = DocumentService.from_default_settings(collection_name)
            document = document_service.get_document(uuid.UUID(document_id))
            serializer = WorkspaceCollectionDocumentSerializer(document)
            return JsonResponse(serializer.data)

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Document not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Update a document",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Title of the document"
                ),
                "content": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Content of the document"
                ),
                "metadata": openapi.Schema(
                    type=openapi.TYPE_OBJECT, description="Metadata of the document"
                ),
            },
            required=["title", "content"],
        ),
        responses={
            200: openapi.Response("Document updated successfully"),
            404: "Document not found",
            400: "Bad request",
        },
    )
    def put(self, request, collection_name, document_id):
        try:
            data = json.loads(request.body)
            title = data.get("title")
            content = data.get("content")
            metadata = data.get("metadata", {})
            user = request.user

            document_service = DocumentService.from_default_settings(collection_name)
            document = document_service.update_document(
                uuid.UUID(document_id), title, content, metadata, user
            )
            serializer = WorkspaceCollectionDocumentSerializer(document)
            return JsonResponse(serializer.data)

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Document not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))

    @swagger_auto_schema(
        operation_description="Delete a document",
        responses={
            204: openapi.Response("Document deleted successfully"),
            404: "Document not found",
            400: "Bad request",
        },
        manual_parameters=[],
    )
    def delete(self, request, collection_name, document_id):
        try:
            document_service = DocumentService.from_default_settings(collection_name)
            document_service.delete_document(uuid.UUID(document_id))
            return JsonResponse(
                {"message": "Document deleted successfully"}, status=204
            )

        except ObjectDoesNotExist:
            return HttpResponseNotFound("Document not found")
        except Exception as e:
            return HttpResponseBadRequest(str(e))
