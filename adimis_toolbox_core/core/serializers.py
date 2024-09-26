import json
import uuid
from json import JSONEncoder
from typing import Dict, Any, Union, List
from langgraph.pregel.types import StateSnapshot
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    ToolMessage,
    SystemMessage,
)


class RunnableConfigEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        if isinstance(obj, RunnableConfig):
            return dict(obj)
        return super().default(obj)


def serialize_runnable_config(config: RunnableConfig) -> str:
    return json.dumps(config, cls=RunnableConfigEncoder)


def __serialize_message(message: BaseMessage) -> Dict[str, Any]:
    """Serialize a message object into a JSON-compatible dictionary."""
    message_type_fields = {
        AIMessage: [
            "invalid_tool_calls",
            "tool_calls",
            "example",
            "usage_metadata",
            "type",
            "id",
        ],
        HumanMessage: ["example", "type", "id"],
        ToolMessage: ["tool_call_id", "artifact", "status", "type", "id"],
        SystemMessage: ["type", "id"],
    }

    serialized = {
        "type": getattr(message, "type", None),
        "content": getattr(message, "content", None),
        "additional_kwargs": getattr(message, "additional_kwargs", {}) or {},
        "response_metadata": getattr(message, "response_metadata", {}) or {},
    }

    for message_type, fields in message_type_fields.items():
        if isinstance(message, message_type):
            serialized.update(
                {field: getattr(message, field, None) for field in fields}
            )
            break

    return serialized


def __is_message(obj: Any) -> bool:
    """Check if the object is a message instance."""
    return isinstance(obj, (AIMessage, HumanMessage, ToolMessage, SystemMessage))


def serialize_non_json(obj: Any) -> Union[Dict[str, Any], List[Any], str]:
    """JSON serializer for objects not serializable by default JSON code."""
    if __is_message(obj):
        return __serialize_message(obj)
    elif isinstance(obj, dict):
        # Properly serialize dictionaries without turning them into lists of key-value pairs
        return {k: serialize_non_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively serialize each item in the list while keeping the list structure
        return [serialize_non_json(item) for item in obj]
    elif isinstance(obj, (int, float, bool, str)) or obj is None:
        # Return the object directly if it's a primitive type
        return obj
    else:
        # Fallback to string conversion for unsupported types
        return str(obj)


def serialize_state_snapshot(snapshot: StateSnapshot) -> Dict[str, Any]:
    """Serialize a StateSnapshot object into a JSON-compatible dictionary."""
    return {
        "values": serialize_non_json(snapshot.values),
        "next": list(snapshot.next),
        "config": serialize_non_json(snapshot.config),
        "metadata": (
            serialize_non_json(snapshot.metadata) if snapshot.metadata else None
        ),
        "created_at": snapshot.created_at,
        "parent_config": (
            serialize_non_json(snapshot.parent_config)
            if snapshot.parent_config
            else None
        ),
    }
