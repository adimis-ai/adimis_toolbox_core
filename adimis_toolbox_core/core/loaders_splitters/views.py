from drf_yasg import openapi
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from .loaders import create_loader, LoadDocumentsRequestSerializer
from .splitters import split_document, SplitDocumentRequestSerializer
from rest_framework.decorators import api_view, permission_classes, parser_classes


@swagger_auto_schema(
    method="post",
    request_body=LoadDocumentsRequestSerializer,
    responses={
        200: openapi.Response(description="Loaded documents"),
        400: openapi.Response(description="Bad request"),
        401: openapi.Response(description="Unauthorized"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def load_documents(request):
    serializer = LoadDocumentsRequestSerializer(data=request.data)
    if serializer.is_valid():
        method = serializer.validated_data["method"]
        if method == "urls":
            loader_props = serializer.validated_data["url_loader_props"]
            loader = create_loader("urls", loader_props)
        elif method == "uploaded_files":
            loader_props = serializer.validated_data["upload_file_loader_props"]
            loader = create_loader("uploaded_files", loader_props)
        else:
            return Response(
                {"error": "Invalid method"}, status=status.HTTP_400_BAD_REQUEST
            )

        documents = loader.load()
        return Response([doc.to_dict() for doc in documents], status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=SplitDocumentRequestSerializer,
    responses={
        200: openapi.Response(description="Split text segments"),
        400: openapi.Response(description="Bad request"),
        401: openapi.Response(description="Unauthorized"),
    },
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, JSONParser])
def split_text(request):
    serializer = SplitDocumentRequestSerializer(data=request.data)
    if serializer.is_valid():
        validated_data = serializer.validated_data
        method = list(validated_data.keys())[0]
        props = validated_data[method]

        try:
            split_texts = split_document(method, props)
            return Response(split_texts, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
