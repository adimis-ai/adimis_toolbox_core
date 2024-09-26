from rest_framework import serializers
from .models import WorkspaceWorkflow, WorkspaceWorkflowThread


class WorkspaceWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceWorkflow
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )


class WorkspaceWorkflowThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceWorkflowThread
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "last_used_by_workflow",
        )
