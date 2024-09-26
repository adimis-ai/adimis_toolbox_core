import json
from .services import CompiledGraphService
from langchain.pydantic_v1 import BaseModel
from channels.generic.websocket import AsyncWebsocketConsumer
from typing import Dict, Any, Sequence, Union, Literal, List, Optional
from ..core import serialize_non_json, RunnableConfig


class GraphStreamRequest(BaseModel):
    graph_name: str
    input: Union[Dict[str, Any], Any]
    config: Optional[RunnableConfig] = None
    stream_mode: Optional[
        Union[
            Literal["values", "updates", "debug"],
            List[Literal["values", "updates", "debug"]],
        ]
    ] = "debug"
    output_keys: Optional[Union[str, Sequence[str]]] = None
    interrupt_before: Optional[Union[Sequence[str], Literal["*"]]] = None
    interrupt_after: Optional[Union[Sequence[str], Literal["*"]]] = None


class GraphStreamConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = CompiledGraphService()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data: str):
        try:
            data = self.__parse_json(text_data)
            request = GraphStreamRequest.parse_obj(data)
            await self.execute_graph(request)
        except Exception as e:
            await self.send_error(str(e))

    async def execute_graph(self, request: GraphStreamRequest):
        try:
            async for res in self.service.stream(
                graph_name=request.graph_name,
                input=request.input,
                config=request.config,
                stream_mode=request.stream_mode,
                output_keys=request.output_keys,
                interrupt_before=request.interrupt_before,
                interrupt_after=request.interrupt_after,
            ):
                await self.send_json({"action": "response", "data": res})

            await self.send_json({"action": "response", "data": "__end__"})
        except Exception as e:
            await self.send_error(f"Graph execution failed: {str(e)}")

    async def send_error(self, message: str):
        await self.send_json({"action": "error", "message": message})

    async def send_json(self, content: Dict[str, Any]):
        await self.send(text_data=json.dumps(content, default=serialize_non_json))

    def __parse_json(self, text_data: str) -> Dict[str, Any]:
        return json.loads(text_data)
