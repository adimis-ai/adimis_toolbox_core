# Adimis Toolbox Code Documentation

## Introduction

**Adimis Toolbox Code** is a Django-based package designed for executing and scheduling graph-based automated workflows while maintaining a knowledge base. This package includes several Django apps that can be easily integrated into your Django projects.

## Installation

To install the `adimis_toolbox_core` package, ensure you have access to the private repository, then use the following command:

```bash
pip install git+https://github.com/adimis-ai/adimis_toolbox_core.git@main#egg=adimis_toolbox_core
```

## Configuration

### 1. Updating Your Django Project's Settings

Add the following settings to your Django project's `settings.py` file:

```python
from typing import Dict
from adimis_toolbox_code.core import GraphRegistryModel
from decouple import config  # If you're using python-decouple for environment variables

OPENAI_API_KEY: str = config("OPENAI_API_KEY")
GOOGLE_API_KEY: str = config("GOOGLE_API_KEY")
OPENAI_AI_MODEL: str = config("OPENAI_AI_MODEL")
GOOGLE_AI_MODEL: str = config("GOOGLE_AI_MODEL")
VECTOR_DB_CONN_STRING: str = config("SUPABASE_DB_CONN_STRING")
VECTOR_DB_EMBEDDING_MODEL: str = config("VECTOR_DB_EMBEDDING_MODEL")
GRAPH_REGISTRY: Dict[str, GraphRegistryModel] = {}
```

### 2. Adding Adimis Toolbox Code Apps to `INSTALLED_APPS`

In your `settings.py`, add the Adimis Toolbox Code apps to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Other Django apps
    "adimis_toolbox_code.core",
    "adimis_toolbox_code.graph_executor",
    "adimis_toolbox_code.knowledge_base",
    "adimis_toolbox_code.cron_jobs",
    "adimis_toolbox_code.members",
    "adimis_toolbox_code.member_permissions",
    "adimis_toolbox_code.workflow_threads",
    "adimis_toolbox_code.workflows",
]
```

### 3. Updating Your Django Project's ASGI Configuration

Edit your `[app_name]/asgi.py` file to include the following setup:

```python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()

from django.urls import path, include
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": URLRouter([path("api/v1/", include("adimis_toolbox_code.graph_executor.consumer_urls"))]),
    }
)
```

### 4. Updating Your Django Project's Main `urls.py` File

```python
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Adimis Toolbox Code",
        default_version="v1",
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
   path("admin/", admin.site.urls),
   path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
   ),
   path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
   path("api/v1/", include("adimis_toolbox_code.graph_executor.urls")),
   path("api/v1/", include("adimis_toolbox_code.knowledge_base.urls")),
   path("api/v1/", include("adimis_toolbox_code.graph_executor.consumer_urls")),
]
```
