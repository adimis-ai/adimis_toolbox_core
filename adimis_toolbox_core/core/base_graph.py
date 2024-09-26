from django.conf import settings
from abc import ABC, abstractmethod
from typing import Any, Coroutine
from .types import (
    DynamicFormProps,
    GraphRegistryModel,
    CompiledStateGraph,
    RunnableConfig,
)


def register_graph(
    graph_name: str,
    inputs_schema: DynamicFormProps,
    default_runnable_config: RunnableConfig,
    runnable_config_schema: DynamicFormProps,
):
    def decorator(cls):
        def wrapper(*args, **kwargs):
            settings.GRAPH_REGISTRY[graph_name] = GraphRegistryModel(
                name=graph_name,
                inputs_schema=inputs_schema,
                runnable_config_schema=runnable_config_schema,
                compiled_state_graph=cls.compile,
                default_runnable_config=default_runnable_config,
            )
            return cls

        return wrapper

    return decorator


class BaseStateGraphBuilder(ABC):
    @abstractmethod
    async def compile(self) -> Coroutine[Any, Any, CompiledStateGraph]:
        pass
