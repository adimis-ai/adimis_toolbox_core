from django.urls import path
from .consumers import GraphStreamConsumer

urlpatterns = [
    path(
        "graph/stream/",
        GraphStreamConsumer.as_asgi(),
        name="graph_stream",
    ),
]
