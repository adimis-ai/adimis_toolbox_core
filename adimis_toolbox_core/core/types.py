import uuid
from django.conf import settings
from langchain_core.runnables import RunnableConfig
from langchain.pydantic_v1 import BaseModel, HttpUrl, Field
from typing import Any, Optional, Literal, Coroutine, Callable, Union, List
from langchain_core.messages import (
    MessageLikeRepresentation,
    RemoveMessage,
    convert_to_messages,
    message_chunk_to_message,
)
from langgraph.graph.state import CompiledStateGraph

Messages = Union[list[MessageLikeRepresentation], MessageLikeRepresentation]


def add_messages(left: Messages, right: Messages) -> Messages:
    """Merges two lists of messages, updating existing messages by ID."""
    if not isinstance(left, list):
        left = [left]
    if not isinstance(right, list):
        right = [right]

    left = [message_chunk_to_message(m) for m in convert_to_messages(left)]
    right = [message_chunk_to_message(m) for m in convert_to_messages(right)]

    for m in left:
        if m.id is None:
            m.id = str(uuid.uuid4())
    for m in right:
        if m.id is None:
            m.id = str(uuid.uuid4())

    existing_contents = {(m.content, type(m)) for m in left}
    left_idx_by_id = {m.id: i for i, m in enumerate(left)}
    merged = left.copy()
    ids_to_remove = set()

    for m in right:
        if (existing_idx := left_idx_by_id.get(m.id)) is not None:
            if isinstance(m, RemoveMessage):
                ids_to_remove.add(m.id)
            else:
                merged[existing_idx] = m
        elif (m.content, type(m)) not in existing_contents:
            if isinstance(m, RemoveMessage):
                raise ValueError(
                    f"Attempting to delete a message with an ID that doesn't exist ('{m.id}')"
                )
            merged.append(m)
            existing_contents.add((m.content, type(m)))

    merged = [m for m in merged if m.id not in ids_to_remove]
    return merged


AsCompiledGraphType = Callable[[], Coroutine[Any, Any, CompiledStateGraph]]

InputType = Union[
    str,
    Literal[
        "markdown",
        "file",
        "select",
        "groupedSelect",
        "array",
        "button",
        "checkbox",
        "color",
        "date",
        "datetime-local",
        "email",
        "file",
        "hidden",
        "image",
        "month",
        "number",
        "password",
        "radio",
        "range",
        "reset",
        "search",
        "submit",
        "tel",
        "text",
        "time",
        "url",
        "week",
        "object",
        "messages",
    ],
]


class Option(BaseModel):
    id: str
    label: str
    value: str


class GroupedOption(BaseModel):
    label: str
    options: List[Option]


class Link(BaseModel):
    url: HttpUrl
    text: str


class ObjectSchema(BaseModel):
    key: str
    type: InputType
    required: bool
    options: Optional[List[Option]] = None


class FieldSchema(BaseModel):
    name: str
    label: str
    type: InputType
    description: Optional[str] = None
    options: List[Option] = Field(default_factory=list)
    groupedOptions: List[GroupedOption] = Field(default_factory=list)
    accept: Optional[str] = None
    width: Optional[str] = "w-full"
    objectSchema: List[ObjectSchema] = Field(default_factory=list)
    disabled: Optional[bool] = False
    link: Optional[Link] = None
    disableGrid: Optional[bool] = False
    required: Optional[bool] = False


class DynamicFormProps(BaseModel):
    form_schema: List[FieldSchema]

    def serialize(self) -> dict:
        return self.dict()

    @classmethod
    def deserialize(cls, data: dict) -> "DynamicFormProps":
        return cls(**data)


class GraphRegistryModel(BaseModel):
    name: str
    inputs_schema: DynamicFormProps
    runnable_config_schema: DynamicFormProps
    default_runnable_config: Optional[RunnableConfig] = {}
    type: Optional[Literal["chatbot", "automation", "all"]] = "all"
    compiled_state_graph: AsCompiledGraphType

    class Config:
        arbitrary_types_allowed = True

    def serialize(self) -> dict:
        return self.dict()

    @classmethod
    def deserialize(cls, data: dict) -> "GraphRegistryModel":
        return cls(**data)


class LLMConfig(BaseModel):
    api_key: Optional[str] = None
    llm_model_name: Optional[str] = None
    provider: Optional[Literal["openai", "openai_chat", "gemini", "gemini_chat"]] = None
    temperature: Optional[float] = 0.0
    timeout: Optional[int] = 30
    max_retries: Optional[int] = 3
    max_tokens: Optional[int] = 1024
    n: Optional[int] = 1
    top_p: Optional[float] = 0.0

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        self.assign_api_key_and_model_name()

    def assign_api_key_and_model_name(self):
        if self.provider in ["openai", "openai_chat"]:
            self.api_key = settings.OPENAI_API_KEY
            self.llm_model_name = settings.OPENAI_AI_MODEL
        elif self.provider in ["gemini", "gemini_chat"]:
            self.api_key = settings.GOOGLE_API_KEY
            self.llm_model_name = settings.GOOGLE_AI_MODEL
