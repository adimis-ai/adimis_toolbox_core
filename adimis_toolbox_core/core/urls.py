from django.urls import path
from .loaders_splitters.views import split_text, load_documents

urlpatterns = [
    path("core/loaders/", load_documents, name="load_documents"),
    path("core/splitters/", split_text, name="split_text"),
]
