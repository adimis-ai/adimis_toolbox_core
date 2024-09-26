from rest_framework import serializers
from .models import WorkspaceCollection, WorkspaceCollectionDocument


class WorkspaceCollectionSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceCollection
        fields = [
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
            }
        return None

    def get_updated_by(self, obj):
        if obj.updated_by:
            return {
                "id": obj.updated_by.id,
                "username": obj.updated_by.username,
            }
        return None


class WorkspaceCollectionDocumentSerializer(serializers.ModelSerializer):
    collection = WorkspaceCollectionSerializer()
    created_by = serializers.SerializerMethodField()
    updated_by = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceCollectionDocument
        fields = [
            "id",
            "title",
            "content",
            "metadata",
            "embeddings",
            "uri",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "collection",
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {
                "id": obj.created_by.id,
                "username": obj.created_by.username,
            }
        return None

    def get_updated_by(self, obj):
        if obj.updated_by:
            return {
                "id": obj.updated_by.id,
                "username": obj.updated_by.username,
            }
        return None
