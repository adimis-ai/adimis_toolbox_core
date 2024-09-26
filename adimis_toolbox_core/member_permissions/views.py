from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import WorkspaceMemberPermission
from .serializers import WorkspaceMemberPermissionSerializer

class WorkspaceMemberPermissionViewSet(viewsets.ModelViewSet):
    queryset = WorkspaceMemberPermission.objects.all()
    serializer_class = WorkspaceMemberPermissionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
