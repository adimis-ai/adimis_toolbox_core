# Generated by Django 5.1 on 2024-08-25 19:51

import django.db.models.deletion
import pgvector.django
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkspaceCollection",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=255, unique=True)),
                ("description", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workspace_collections_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workspace_collections_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="WorkspaceCollectionDocument",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(db_index=True, max_length=255)),
                ("content", models.TextField()),
                ("metadata", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("embeddings", pgvector.django.VectorField(blank=True, null=True)),
                (
                    "collection",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="workspace_collection_documents",
                        to="knowledge_base.workspacecollection",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workspace_documents_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="workspace_documents_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["title"],
            },
        ),
        migrations.AddIndex(
            model_name="workspacecollection",
            index=models.Index(fields=["created_by"], name="idx_ws_coll_created_by"),
        ),
        migrations.AddIndex(
            model_name="workspacecollection",
            index=models.Index(fields=["updated_by"], name="idx_ws_coll_updated_by"),
        ),
        migrations.AddIndex(
            model_name="workspacecollectiondocument",
            index=models.Index(
                fields=["collection_id"], name="idx_ws_coll_doc_coll_id"
            ),
        ),
        migrations.AddIndex(
            model_name="workspacecollectiondocument",
            index=models.Index(
                fields=["created_by"], name="idx_ws_coll_doc_created_by"
            ),
        ),
        migrations.AddIndex(
            model_name="workspacecollectiondocument",
            index=models.Index(fields=["embeddings"], name="idx_ws_coll_doc_embed"),
        ),
        migrations.AddIndex(
            model_name="workspacecollectiondocument",
            index=models.Index(fields=["title"], name="idx_ws_coll_doc_title"),
        ),
        migrations.AddIndex(
            model_name="workspacecollectiondocument",
            index=models.Index(
                fields=["updated_by"], name="idx_ws_coll_doc_updated_by"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="workspacecollectiondocument",
            unique_together={("collection", "title")},
        ),
    ]
