from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceMemberPermissionViewSet

router = DefaultRouter()
router.register(r'permissions', WorkspaceMemberPermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
