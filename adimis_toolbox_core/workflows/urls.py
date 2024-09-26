from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceWorkflowViewSet, WorkspaceWorkflowThreadViewSet

router = DefaultRouter()
router.register(r"workflows", WorkspaceWorkflowViewSet)
router.register(r"workflow-threads", WorkspaceWorkflowThreadViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
