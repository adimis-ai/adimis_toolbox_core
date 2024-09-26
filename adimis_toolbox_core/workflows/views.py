from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WorkspaceWorkflow, WorkspaceWorkflowThread
from .serializers import WorkspaceWorkflowSerializer, WorkspaceWorkflowThreadSerializer


class WorkspaceWorkflowViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceWorkflow.objects.all()
    serializer_class = WorkspaceWorkflowSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class WorkspaceWorkflowThreadViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceWorkflowThread.objects.all()
    serializer_class = WorkspaceWorkflowThreadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
