from django.contrib import admin
from .models import WorkspaceMemberPermission

@admin.register(WorkspaceMemberPermission)
class WorkspaceMemberPermissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'workspace_member', 
        'is_active', 
        'created_at', 
        'updated_at', 
        'created_by', 
        'updated_by'
    )
    search_fields = ('workspace_member__user__username',)
    list_filter = ('is_active', 'created_at', 'updated_at')
    filter_horizontal = (
        'allowed_workflows', 
        'allowed_collections', 
        'allowed_collection_documents'
    )
