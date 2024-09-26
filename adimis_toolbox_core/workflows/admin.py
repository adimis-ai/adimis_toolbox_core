from django.contrib import admin
from .models import WorkspaceWorkflow


@admin.register(WorkspaceWorkflow)
class WorkspaceWorkflowAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_workspace_id",
        "name",
        "graph_name",
        "is_active",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    search_fields = ("name", "client_workspace_id", "graph_name")
    list_filter = ("is_active", "created_at", "updated_at")
