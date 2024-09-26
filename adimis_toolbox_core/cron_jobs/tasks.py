from celery import shared_task
from ..core import RunnableConfig
from ..graph_executor.services import CompiledGraphService
from typing import Any, Dict, List, Optional, Union, Sequence, Literal

@shared_task(bind=True, max_retries=20)
async def execute_graph(
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
    try:
        return await CompiledGraphService().invoke(
            graph_name=graph_name,
            input=input,
            config=config,
            stream_mode=stream_mode,
            output_keys=output_keys,
            interrupt_before=interrupt_before,
            interrupt_after=interrupt_after,
        )
    except Exception as exc:
        countdown = 2 ** self.request.retries
        raise self.retry(exc=exc, countdown=countdown)
