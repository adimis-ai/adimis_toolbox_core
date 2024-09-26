import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class WorkspaceMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_workspace_id = models.UUIDField(null=False, blank=False, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="workspace_members_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="workspace_members_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["client_workspace_id"], name="idx_ws_mem_cl_ws_id"),
        ]

    def __str__(self):
        return str(self.id)
