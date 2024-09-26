import uuid
import asyncpg
from django.db import connection
from django.conf import settings
from django.db import transaction
from django.utils.text import slugify
from asgiref.sync import sync_to_async
from django.db.models import Case, When
from typing import Optional, TypedDict, List
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from .models import WorkspaceCollectionDocument, WorkspaceCollection
from .serializers import (
    WorkspaceCollectionSerializer,
    WorkspaceCollectionDocumentSerializer,
)


class DocumentResponse(TypedDict):
    count: int
    response: List[WorkspaceCollectionDocument]


class CollectionService:
    @staticmethod
    def create_collection(name: str, description: str, user) -> WorkspaceCollection:
        with transaction.atomic():
            collection = WorkspaceCollection.objects.create(
                name=slugify(name),
                description=description,
                created_by=user,
                updated_by=user,
            )
            return collection

    @staticmethod
    async def acreate_collection(
        name: str, description: str, user
    ) -> WorkspaceCollection:
        async with transaction.atomic():
            collection = await WorkspaceCollection.objects.acreate(
                name=slugify(name),
                description=description,
                created_by=user,
                updated_by=user,
            )
            return collection

    @staticmethod
    def get_collection(collection_id: uuid.UUID) -> dict:
        collection = WorkspaceCollection.objects.get(id=collection_id)
        return WorkspaceCollectionSerializer(collection).data

    @staticmethod
    async def aget_collection(collection_id: uuid.UUID) -> dict:
        collection = await WorkspaceCollection.objects.aget(id=collection_id)
        return WorkspaceCollectionSerializer(collection).data

    @staticmethod
    def get_collection_by_name(name: str) -> dict:
        collection = WorkspaceCollection.objects.get(name=name)
        return WorkspaceCollectionSerializer(collection).data

    @staticmethod
    async def aget_collection_by_name(name: str) -> dict:
        collection = await WorkspaceCollection.objects.aget(name=name)
        return WorkspaceCollectionSerializer(collection).data

    @staticmethod
    def get_all_collections(
        workspace_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> dict:
        queryset = WorkspaceCollection.objects.filter(
            workspace_id=workspace_id
        ).order_by("updated_at")
        count = queryset.count()
        collections = WorkspaceCollectionSerializer(
            queryset[offset : offset + limit], many=True
        ).data
        return {"count": count, "response": collections}

    @staticmethod
    async def aget_all_collections(
        workspace_id: uuid.UUID, limit: int = 10, offset: int = 0
    ) -> dict:
        queryset = WorkspaceCollection.objects.filter(
            workspace_id=workspace_id
        ).order_by("updated_at")
        count = await sync_to_async(queryset.count)()
        collections = WorkspaceCollectionSerializer(
            await queryset[offset : offset + limit].all(), many=True
        ).data
        return {"count": count, "response": collections}

    @staticmethod
    def update_collection(
        collection_id: uuid.UUID,
        name: str,
        description: str,
        user,
        workspace_id: uuid.UUID,
    ) -> WorkspaceCollection:
        with transaction.atomic():
            collection = WorkspaceCollection.objects.get(id=collection_id)
            collection.name = slugify(name)
            collection.description = description
            collection.updated_by = user
            collection.save()
            return collection

    @staticmethod
    async def aupdate_collection(
        collection_id: uuid.UUID,
        name: str,
        description: str,
        user,
        workspace_id: uuid.UUID,
    ) -> WorkspaceCollection:
        async with transaction.atomic():
            collection = await WorkspaceCollection.objects.aget(id=collection_id)
            collection.name = slugify(name)
            collection.description = description
            collection.updated_by = user
            await collection.asave()
            return collection

    @staticmethod
    def delete_collection(collection_id: uuid.UUID) -> None:
        with transaction.atomic():
            collection = WorkspaceCollection.objects.get(id=collection_id)
            collection.delete()

    @staticmethod
    async def adelete_collection(collection_id: uuid.UUID) -> None:
        async with transaction.atomic():
            collection = await WorkspaceCollection.objects.aget(id=collection_id)
            await collection.adelete()

    @staticmethod
    def reset_collection(collection_id: uuid.UUID) -> None:
        with transaction.atomic():
            collection = WorkspaceCollection.objects.get(id=collection_id)
            WorkspaceCollectionDocument.objects.filter(collection=collection).delete()

    @staticmethod
    async def areset_collection(collection_id: uuid.UUID) -> None:
        async with transaction.atomic():
            collection = await WorkspaceCollection.objects.aget(id=collection_id)
            await WorkspaceCollectionDocument.objects.filter(
                collection=collection
            ).adelete()


class DocumentService:
    def __init__(
        self,
        collection_name: str,
        embeddings: Embeddings,
        pool: Optional[asyncpg.Pool] = None,
    ):
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.collection: WorkspaceCollection | None = None
        self.pool = pool

    @classmethod
    def from_default_settings(cls, collection_name: str):
        embeddings = OpenAIEmbeddings(
            model=settings.VECTOR_DB_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
        instance = cls(
            collection_name=collection_name,
            embeddings=embeddings,
            pool=None,
        )
        instance.collection = instance._get_collection_by_name(
            collection_name=collection_name
        )
        return instance

    @classmethod
    async def afrom_default_settings(cls, collection_name: str):
        pool = await asyncpg.create_pool(
            dsn=f"postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@"
            f"{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']}",
            min_size=1,
            max_size=10,
            statement_cache_size=0,
        )

        self = cls(
            collection_name=collection_name,
            embeddings=None,
            pool=pool,
        )

        self.collection = await self._aget_collection_by_name(
            collection_name=collection_name
        )
        self.embeddings = OpenAIEmbeddings(
            model=settings.VECTOR_DB_EMBEDDING_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

        return self

    def _get_collection_by_name(self, collection_name: str) -> WorkspaceCollection:
        return WorkspaceCollection.objects.get(name=collection_name)

    async def _aget_collection_by_name(
        self, collection_name: str
    ) -> WorkspaceCollection:
        return await sync_to_async(WorkspaceCollection.objects.get)(
            name=collection_name
        )

    def create_document(
        self,
        title: str,
        content: str,
        metadata: dict,
        user,
    ) -> WorkspaceCollectionDocument:
        with transaction.atomic():
            document = WorkspaceCollectionDocument.objects.create(
                collection=self.collection,
                title=slugify(title),
                content=content,
                metadata=metadata,
                created_by=user,
                updated_by=user,
            )
            document.save()
            return document

    async def acreate_document(
        self,
        title: str,
        content: str,
        metadata: dict,
        user,
    ) -> WorkspaceCollectionDocument:
        async with transaction.atomic():
            document = await WorkspaceCollectionDocument.objects.acreate(
                collection=self.collection,
                title=slugify(title),
                content=content,
                metadata=metadata,
                created_by=user,
                updated_by=user,
            )
            await document.asave()
            return document

    def update_document(
        self,
        document_id: uuid.UUID,
        title: str,
        content: str,
        metadata: dict,
        user,
    ) -> WorkspaceCollectionDocument:
        with transaction.atomic():
            document = WorkspaceCollectionDocument.objects.get(
                id=document_id, collection=self.collection
            )
            document.title = slugify(title)
            document.content = content
            document.metadata = metadata
            document.updated_by = user
            document.save()
            return document

    async def aupdate_document(
        self,
        document_id: uuid.UUID,
        title: str,
        content: str,
        metadata: dict,
        user,
    ) -> WorkspaceCollectionDocument:
        async with transaction.atomic():
            document = await WorkspaceCollectionDocument.objects.aget(
                id=document_id, collection=self.collection
            )
            document.title = slugify(title)
            document.content = content
            document.metadata = metadata
            document.updated_by = user
            await document.asave()
            return document

    def get_document(self, document_id: uuid.UUID) -> dict:
        document = WorkspaceCollectionDocument.objects.get(
            id=document_id, collection=self.collection
        )
        return WorkspaceCollectionDocumentSerializer(document).data

    async def aget_document(self, document_id: uuid.UUID) -> dict:
        document = await WorkspaceCollectionDocument.objects.aget(
            id=document_id, collection=self.collection
        )
        return WorkspaceCollectionDocumentSerializer(document).data

    def get_all_documents(self, limit: int = 10, offset: int = 0) -> dict:
        queryset = WorkspaceCollectionDocument.objects.filter(
            collection=self.collection
        ).order_by("updated_at")
        count = queryset.count()
        documents = WorkspaceCollectionDocumentSerializer(
            queryset[offset : offset + limit], many=True
        ).data
        return {"count": count, "response": documents}

    async def aget_all_documents(self, limit: int = 10, offset: int = 0) -> dict:
        queryset = WorkspaceCollectionDocument.objects.filter(
            collection=self.collection
        ).order_by("updated_at")
        count = await sync_to_async(queryset.count)()
        documents = WorkspaceCollectionDocumentSerializer(
            await queryset[offset : offset + limit].all(), many=True
        ).data
        return {"count": count, "response": documents}

    def delete_document(self, document_id: uuid.UUID) -> None:
        with transaction.atomic():
            document = WorkspaceCollectionDocument.objects.get(
                id=document_id, collection=self.collection
            )
            document.delete()

    async def adelete_document(self, document_id: uuid.UUID) -> None:
        async with transaction.atomic():
            document = await WorkspaceCollectionDocument.objects.aget(
                id=document_id, collection=self.collection
            )
            await document.adelete()

    def bulk_create_documents(
        self,
        documents: list[dict],
        user,
    ) -> list[WorkspaceCollectionDocument]:
        with transaction.atomic():
            created_documents = []
            for doc in documents:
                document = WorkspaceCollectionDocument(
                    collection=self.collection,
                    title=doc["title"],
                    content=doc["content"],
                    metadata=doc.get("metadata", {}),
                    created_by=user,
                    updated_by=user,
                )
                document.save()
                created_documents.append(document)
            return created_documents

    async def abulk_create_documents(
        self,
        documents: list[dict],
        user,
    ) -> list[WorkspaceCollectionDocument]:
        async with transaction.atomic():
            created_documents = []
            for doc in documents:
                document = WorkspaceCollectionDocument(
                    collection=self.collection,
                    title=doc["title"],
                    content=doc["content"],
                    metadata=doc.get("metadata", {}),
                    created_by=user,
                    updated_by=user,
                )
                await document.asave()
                created_documents.append(document)
            return created_documents

    def bulk_update_documents(
        self,
        documents: list[dict],
        user,
    ) -> list[WorkspaceCollectionDocument]:
        with transaction.atomic():
            updated_documents = []
            for doc in documents:
                document = WorkspaceCollectionDocument.objects.get(
                    id=doc["id"], collection=self.collection
                )
                document.title = doc["title"]
                document.content = doc["content"]
                document.metadata = doc.get("metadata", {})
                document.updated_by = user
                document.save()
                updated_documents.append(document)
            return updated_documents

    async def abulk_update_documents(
        self,
        documents: list[dict],
        user,
    ) -> list[WorkspaceCollectionDocument]:
        async with transaction.atomic():
            updated_documents = []
            for doc in documents:
                document = await WorkspaceCollectionDocument.objects.aget(
                    id=doc["id"], collection=self.collection
                )
                document.title = doc["title"]
                document.content = doc["content"]
                document.metadata = doc.get("metadata", {})
                document.updated_by = user
                await document.asave()
                updated_documents.append(document)
            return updated_documents

    def bulk_delete_documents(self, document_ids: list[str]) -> None:
        with transaction.atomic():
            WorkspaceCollectionDocument.objects.filter(
                id__in=document_ids, collection=self.collection
            ).delete()

    async def abulk_delete_documents(self, document_ids: list[str]) -> None:
        async with transaction.atomic():
            await WorkspaceCollectionDocument.objects.filter(
                id__in=document_ids, collection=self.collection
            ).adelete()

    def similarity_search(
        self, query: str, top_k: int = 10
    ) -> list[WorkspaceCollectionDocument]:
        query_embedding = self.embeddings.embed_query(query)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, 
                    embeddings <-> %s::vector AS distance 
                FROM knowledge_base_workspacecollectiondocument 
                WHERE collection_id = %s 
                ORDER BY distance 
                LIMIT %s
                """,
                [query_embedding, self.collection.id, top_k],
            )
            results = cursor.fetchall()

        document_ids = [result[0] for result in results]
        documents = list(
            WorkspaceCollectionDocument.objects.filter(id__in=document_ids).order_by(
                Case(
                    *[
                        When(id=doc_id, then=pos)
                        for pos, doc_id in enumerate(document_ids)
                    ]
                )
            )
        )
        return documents

    def similarity_search_with_relevance_scores(
        self, query: str, top_k: int = 10
    ) -> list[tuple[WorkspaceCollectionDocument, float]]:
        query_embedding = self.embeddings.embed_query(query)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, 
                       embeddings <-> %s::vector AS distance
                FROM knowledge_base_workspacecollectiondocument 
                WHERE collection_id = %s 
                ORDER BY distance 
                LIMIT %s
                """,
                [query_embedding, self.collection.id, top_k],
            )
            results = cursor.fetchall()

        documents_with_relevance = []
        for result in results:
            document_id, distance = result
            document = WorkspaceCollectionDocument.objects.get(id=document_id)
            documents_with_relevance.append((document, distance))

        return documents_with_relevance

    async def asimilarity_search(
        self, query: str, top_k: int = 10
    ) -> list[WorkspaceCollectionDocument]:
        query_embedding = await self.embeddings.aembed_query(query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT id, 
                    embeddings <-> $1::vector AS distance 
                FROM knowledge_base_workspacecollectiondocument 
                WHERE collection_id = $2 
                ORDER BY distance 
                LIMIT $3
                """,
                query_embedding_str,
                self.collection.id,
                top_k,
            )

        document_ids = [result["id"] for result in results]
        queryset = WorkspaceCollectionDocument.objects.filter(id__in=document_ids)
        documents = await sync_to_async(list)(
            queryset.order_by(
                Case(
                    *[
                        When(id=doc_id, then=pos)
                        for pos, doc_id in enumerate(document_ids)
                    ]
                )
            )
        )

        return documents

    async def asimilarity_search_with_relevance_scores(
        self, query: str, top_k: int = 10
    ) -> list[tuple[WorkspaceCollectionDocument, float]]:
        query_embedding = await self.embeddings.aembed_query(query)
        query_embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

        async with self.pool.acquire() as conn:
            results = await conn.fetch(
                """
                SELECT id, 
                    embeddings <-> $1::vector AS distance
                FROM knowledge_base_workspacecollectiondocument 
                WHERE collection_id = $2 
                ORDER BY distance 
                LIMIT $3
                """,
                query_embedding_str,
                self.collection.id,
                top_k,
            )

        document_ids = [result["id"] for result in results]
        distances = [result["distance"] for result in results]
        queryset = WorkspaceCollectionDocument.objects.filter(id__in=document_ids)
        documents = await sync_to_async(list)(
            queryset.order_by(
                Case(
                    *[
                        When(id=doc_id, then=pos)
                        for pos, doc_id in enumerate(document_ids)
                    ]
                )
            )
        )
        documents_with_relevance = [
            (document, distance) for document, distance in zip(documents, distances)
        ]

        return documents_with_relevance
