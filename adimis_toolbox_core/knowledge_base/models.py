import uuid
from django.db import models
from django.conf import settings
from pgvector.django import VectorField
from langchain_openai import OpenAIEmbeddings
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class WorkspaceCollection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255, unique=True, null=False, blank=False, db_index=True
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="workspace_collections_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="workspace_collections_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(WorkspaceCollection, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class WorkspaceCollectionDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection = models.ForeignKey(
        WorkspaceCollection,
        related_name="workspace_collection_documents",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    metadata = models.JSONField(null=True, blank=True)
    embeddings = VectorField(null=True, blank=True)
    uri = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        related_name="workspace_documents_created",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    updated_by = models.ForeignKey(
        User,
        related_name="workspace_documents_updated",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        self.title = slugify(self.title)
        if self._state.adding or "content" in self.get_dirty_fields(
            check_relationship=True
        ):
            try:
                embeddings_service = OpenAIEmbeddings(
                    model=settings.VECTOR_DB_EMBEDDING_MODEL,
                    api_key=settings.OPENAI_API_KEY,
                )
                embeddings = embeddings_service.embed_documents([self.content])
                if embeddings and len(embeddings) == 1:
                    self.embeddings = embeddings[0]
                else:
                    raise ValueError(
                        "Failed to generate embeddings or returned incorrect format."
                    )
            except Exception as e:
                raise ValueError(f"Error generating embeddings: {e}")

        super(WorkspaceCollectionDocument, self).save(*args, **kwargs)

    def __str__(self):
        return self.title
