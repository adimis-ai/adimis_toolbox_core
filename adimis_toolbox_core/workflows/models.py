import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class WorkspaceWorkflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_workspace_id = models.UUIDField(null=False, blank=False, db_index=True)
    name = models.CharField(max_length=255, unique=True, null=False, blank=False)
    description = models.TextField(blank=True, null=True)
    graph_name = models.CharField(max_length=255, null=False, blank=False)
    default_workflow_inputs = models.JSONField(null=True, blank=True)
    workflow_runnable_config = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="workspace_workflows_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="workspace_workflows_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["client_workspace_id"], name="idx_ws_wf_cl_ws_id"),
            models.Index(fields=["name"], name="idx_ws_wf_name"),
        ]

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(WorkspaceWorkflow, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class WorkspaceWorkflowThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_workspace_id = models.UUIDField(null=False, blank=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_by_workflow = models.CharField(max_length=255, null=False, blank=False)

    class Meta:
        indexes = [
            models.Index(fields=["client_workspace_id"], name="idx_ws_wf_th_cl_workspace_id"),
        ]

    def __str__(self):
        return str(self.id)
