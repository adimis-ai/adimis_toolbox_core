from .services import DocumentService
from .serializers import WorkspaceCollectionDocumentSerializer
from asgiref.sync import sync_to_async
from typing import Optional, List, Literal
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun


class PgVectorRetriever(BaseRetriever):
    collection_name: str
    k: Optional[int] = 50
    search_type: Optional[
        Literal["similarity_search", "similarity_search_with_relevance_scores"]
    ] = "similarity_search"

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        if self.search_type == "similarity_search":
            return self._similarity_search(query, run_manager=run_manager)
        elif self.search_type == "similarity_search_with_relevance_scores":
            return self._similarity_search_with_relevance_scores(
                query, run_manager=run_manager
            )
        else:
            raise ValueError("Invalid search type")

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        if self.search_type == "similarity_search":
            return await self._asimilarity_search(query, run_manager=run_manager)
        elif self.search_type == "similarity_search_with_relevance_scores":
            return await self._asimilarity_search_with_relevance_scores(
                query, run_manager=run_manager
            )
        else:
            raise ValueError("Invalid search type")

    def _similarity_search(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        try:
            print(f"Starting similarity search for query: {query}")

            document_service = DocumentService.from_default_settings(
                collection_name=self.collection_name
            )
            print(
                f"DocumentService initialized with collection: {self.collection_name}"
            )

            response = document_service.similarity_search(
                query=query,
                top_k=self.k,
            )
            print("Similarity search completed. Processing response documents.")

            serialized_docs = WorkspaceCollectionDocumentSerializer(
                response, many=True
            ).data

            documents = [
                Document(
                    page_content=doc["content"],
                    metadata=doc,
                )
                for doc in serialized_docs
            ]
            print(f"Processed {len(documents)} documents from response.")

            run_manager.on_retriever_end(documents=documents)
            return documents

        except Exception as e:
            print(f"Error occurred during similarity search: {e}")
            run_manager.on_retriever_error(error=e)
            raise e

    def _similarity_search_with_relevance_scores(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        try:
            document_service = DocumentService.from_default_settings(
                collection_name=self.collection_name
            )
            response = document_service.similarity_search_with_relevance_scores(
                query=query,
                top_k=self.k,
            )

            serialized_docs = [
                {
                    **WorkspaceCollectionDocumentSerializer(doc).data,
                    "relevance_score": score,
                }
                for doc, score in response
            ]

            documents = [
                Document(
                    page_content=doc["content"],
                    metadata=doc,
                )
                for doc in serialized_docs
            ]

            run_manager.on_retriever_end(documents=documents)
            return documents

        except Exception as e:
            run_manager.on_retriever_error(error=e)
            raise e

    async def _asimilarity_search(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        try:
            print(f"Starting async similarity search for query: {query}")

            document_service = await DocumentService.afrom_default_settings(
                collection_name=self.collection_name
            )
            print(
                f"DocumentService initialized with collection: {self.collection_name}"
            )

            response = await document_service.asimilarity_search(
                query=query,
                top_k=self.k,
            )
            print("Async similarity search completed. Processing response documents.")

            serialized_docs = await sync_to_async(
                lambda: WorkspaceCollectionDocumentSerializer(response, many=True).data
            )()

            documents = [
                Document(
                    page_content=doc["content"],
                    metadata=doc,
                )
                for doc in serialized_docs
            ]
            print(f"Processed {len(documents)} documents from response asynchronously.")

            await run_manager.on_retriever_end(documents=documents)
            return documents

        except Exception as e:
            print(f"Error occurred during async similarity search: {e}")
            await run_manager.on_retriever_error(error=e)
            raise e

    async def _asimilarity_search_with_relevance_scores(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        try:
            document_service = await DocumentService.afrom_default_settings(
                collection_name=self.collection_name
            )
            response = await document_service.asimilarity_search_with_relevance_scores(
                query=query,
                top_k=self.k,
            )

            serialized_docs = await sync_to_async(
                lambda: [
                    {
                        **WorkspaceCollectionDocumentSerializer(doc).data,
                        "relevance_score": score,
                    }
                    for doc, score in response
                ]
            )()

            documents = [
                Document(
                    page_content=doc["content"],
                    metadata=doc,
                )
                for doc in serialized_docs
            ]

            await run_manager.on_retriever_end(documents=documents)
            return documents

        except Exception as e:
            await run_manager.on_retriever_error(error=e)
            raise e
