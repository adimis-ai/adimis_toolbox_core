import uuid
from django.db import models
from django.contrib.auth import get_user_model
from ..members.models import WorkspaceMember
from ..workflows.models import WorkspaceWorkflow
from ..knowledge_base.models import WorkspaceCollection, WorkspaceCollectionDocument

User = get_user_model()


class WorkspaceMemberPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace_member = models.ForeignKey(
        WorkspaceMember,
        related_name="workspace_member_permissions",
        on_delete=models.CASCADE,
        db_index=True,
    )
    allowed_graphs = models.JSONField(null=True, blank=True)
    allowed_app_actions = models.JSONField(null=False, blank=False)
    allowed_workflows = models.ManyToManyField(
        WorkspaceWorkflow,
        related_name="permissions",
        blank=True,
    )
    allowed_collections = models.ManyToManyField(
        WorkspaceCollection,
        related_name="permissions",
        blank=True,
    )
    allowed_collection_documents = models.ManyToManyField(
        WorkspaceCollectionDocument,
        related_name="permissions",
        blank=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="workspace_member_permissions_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="workspace_member_permissions_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["workspace_member"], name="idx_ws_mem_perm_ws_mem_id"),
            models.Index(fields=["is_active"], name="idx_ws_mem_perm_active"),
        ]

    def __str__(self):
        return str(self.id)
