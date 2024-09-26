from django.urls import path
from .views import (
    CollectionListCreateView,
    CollectionDetailView,
    DocumentListCreateView,
    DocumentDetailView,
    ResetCollectionView,
)

urlpatterns = [
    path(
        "collections/",
        CollectionListCreateView.as_view(),
        name="collection-list-create",
    ),
    path(
        "collections/<str:collection_name>/",
        CollectionDetailView.as_view(),
        name="collection-detail",
    ),
    path(
        "collections/<str:collection_name>/reset/",
        ResetCollectionView.as_view(),
        name="collection-reset",
    ),
    path(
        "documents/<str:collection_name>/",
        DocumentListCreateView.as_view(),
        name="document-list-create",
    ),
    path(
        "documents/<str:collection_name>/<uuid:document_id>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
]
