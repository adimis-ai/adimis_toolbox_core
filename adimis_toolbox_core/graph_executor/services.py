from django.conf import settings
from typing import Any, Dict, List, Optional, Union, Sequence, Literal
from ..core import (
    GraphRegistryModel,
    StateSnapshot,
    RunnableConfig,
)


class CompiledGraphService:
    def __init__(self) -> None:
        self.registry: Dict[str, GraphRegistryModel] = settings.GRAPH_REGISTRY

    async def __get_compiled_graph(self, graph_name: str):
        graph = self.registry.get(graph_name)
        if not graph:
            raise ValueError(f"Graph '{graph_name}' not found in registry.")
        return await graph.compiled_state_graph()

    async def get_graph_schemas(self, graph_name: str):
        graph = self.registry.get(graph_name)
        compiled_graph = await self.__get_compiled_graph(graph_name)
        if not graph:
            raise ValueError(f"Graph '{graph_name}' not found in registry.")
        graph_prev = compiled_graph.get_graph()

        graph_prev_serializable = {
            "nodes": {
                node_id: {
                    "name": node.name,
                    "data": str(node.data),
                    "metadata": node.metadata,
                }
                for node_id, node in graph_prev.nodes.items()
            },
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "data": edge.data,
                    "conditional": edge.conditional,
                }
                for edge in graph_prev.edges
            ],
        }

        graph_prev_serializable["nodes"] = {
            key: value.dict() if hasattr(value, "dict") else value
            for key, value in graph_prev_serializable["nodes"].items()
        }

        return {
            "graph_name": graph.name,
            "type": graph.type,
            "graph_preview": graph_prev_serializable,
            "inputs_schema": (
                graph.inputs_schema.dict()
                if hasattr(graph.inputs_schema, "dict")
                else graph.inputs_schema
            ),
            "runnable_config_schema": (
                graph.runnable_config_schema.dict()
                if hasattr(graph.runnable_config_schema, "dict")
                else graph.runnable_config_schema
            ),
            "default_runnable_config": graph.default_runnable_config,
        }

    async def get_state_history(self, graph_name: str, config: RunnableConfig):
        states: List[StateSnapshot] = []
        compiled_graph = await self.__get_compiled_graph(graph_name)
        async for snapshot in compiled_graph.aget_state_history(config=config):
            states.append(snapshot)
        return states

    async def get_state(self, graph_name: str, config: RunnableConfig):
        compiled_graph = await self.__get_compiled_graph(graph_name=graph_name)
        return await compiled_graph.aget_state(config=config)

    async def updated_state(
        self,
        graph_name: str,
        config: RunnableConfig,
        values: Dict[str, Any],
        as_node: Optional[str] = None,
    ):
        compiled_graph = await self.__get_compiled_graph(graph_name=graph_name)
        return await compiled_graph.aupdate_state(
            config=config, values=values, as_node=as_node
        )

    async def invoke(
        self,
        graph_name: str,
        input: Union[Dict[str, Any], Any],
        config: Optional[RunnableConfig] = None,
        stream_mode: Optional[
            Union[
                Literal["values", "updates", "debug"],
                List[Literal["values", "updates", "debug"]],
            ]
        ] = "debug",
        output_keys: Optional[Union[str, Sequence[str]]] = None,
        interrupt_before: Optional[Union[Sequence[str], Literal["*"]]] = None,
        interrupt_after: Optional[Union[Sequence[str], Literal["*"]]] = None,
    ):
        compiled_graph = await self.__get_compiled_graph(graph_name=graph_name)
        return await compiled_graph.ainvoke(
            input=input,
            config=config,
            stream_mode=stream_mode,
            output_keys=output_keys,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
        )

    async def stream(
        self,
        graph_name: str,
        input: Union[Dict[str, Any], Any],
        config: Optional[RunnableConfig] = None,
        stream_mode: Optional[
            Union[
                Literal["values", "updates", "debug"],
                List[Literal["values", "updates", "debug"]],
            ]
        ] = "debug",
        output_keys: Optional[Union[str, Sequence[str]]] = None,
        interrupt_before: Optional[Union[Sequence[str], Literal["*"]]] = None,
        interrupt_after: Optional[Union[Sequence[str], Literal["*"]]] = None,
    ):
        compiled_graph = await self.__get_compiled_graph(graph_name=graph_name)
        async for result in compiled_graph.astream(
            input=input,
            config=config,
            stream_mode=stream_mode,
            output_keys=output_keys,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
        ):
            yield result

    async def get_all_graph_schemas(self) -> List[Dict[str, Any]]:
        schemas = []
        try:
            for graph_name in self.registry.keys():
                try:
                    print(f"Retrieving schema for graph: {graph_name}")
                    schema = await self.get_graph_schemas(graph_name)
                    schemas.append(schema)
                    print(f"Successfully retrieved schema for graph: {graph_name}")
                except Exception as e:
                    print(f"Error retrieving schema for graph: {graph_name}")
                    print(f"Error: {e}")
        except Exception as e:
            print("An error occurred while retrieving all graph schemas.")
            print(f"Error: {e}")
        return schemas
