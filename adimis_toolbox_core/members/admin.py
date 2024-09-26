from django.contrib import admin
from .models import WorkspaceMember


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "client_workspace_id",
        "is_active",
        "created_at",
        "updated_at",
        "created_by",
        "updated_by",
    )
    search_fields = ("client_workspace_id",)
    list_filter = ("is_active", "created_at", "updated_at")
