from django.urls import path, re_path
from .views.state_history_view import StateHistoryView
from .views.graph_schemas_view import GraphSchemasView
from .views.state_view import StateView
from .views.update_state_view import UpdateStateView
from .views.invoke_view import InvokeGraphView
from .views.schedule_view import ScheduleGraphView
from .views.all_graphs_view import AllGraphsView

urlpatterns = [
    path(
        "graphs/state-history/",
        StateHistoryView.as_view(),
        name="state_history",
    ),
    path(
        "graphs/<str:graph_name>/schemas/",
        GraphSchemasView.as_view(),
        name="graph_schemas",
    ),
    path(
        "graphs/<str:graph_name>/state/",
        StateView.as_view(),
        name="state",
    ),
    path(
        "graphs/<str:graph_name>/update-state/",
        UpdateStateView.as_view(),
        name="update_state",
    ),
    path(
        "graphs/<str:graph_name>/invoke/",
        InvokeGraphView.as_view(),
        name="invoke_graph",
    ),
    path(
        "graphs/<str:graph_name>/schedule/",
        ScheduleGraphView.as_view(),
        name="schedule_graph",
    ),
    path(
        "graphs/list/",
        AllGraphsView.as_view(),
        name="all_graphs",
    ),
]
