from rest_framework import serializers
from .models import WorkspaceMemberPermission

class WorkspaceMemberPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMemberPermission
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
