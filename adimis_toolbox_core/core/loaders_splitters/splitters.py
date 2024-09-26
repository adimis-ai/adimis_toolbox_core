from rest_framework import serializers
from langchain.pydantic_v1 import BaseModel, Field
from langchain_text_splitters import (
    HTMLHeaderTextSplitter,
    HTMLSectionSplitter,
    CharacterTextSplitter,
    MarkdownHeaderTextSplitter,
    RecursiveJsonSplitter,
    RecursiveCharacterTextSplitter,
    Language,
)
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from typing import List, Tuple, Optional, Literal, Union, Callable


class HTMLHeaderSplitterModelSerializer(serializers.Serializer):
    html_string = serializers.CharField()
    headers_to_split_on = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        required=False,
    )
    split_recursively = serializers.BooleanField(default=False)
    chunk_size = serializers.IntegerField(default=500)
    chunk_overlap = serializers.IntegerField(default=30)


class HTMLSectionSplitterModelSerializer(serializers.Serializer):
    html_string = serializers.CharField()
    headers_to_split_on = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        required=False,
    )
    split_recursively = serializers.BooleanField(default=False)
    chunk_size = serializers.IntegerField(default=500)
    chunk_overlap = serializers.IntegerField(default=30)


class CharacterSplitterModelSerializer(serializers.Serializer):
    text = serializers.CharField()
    separator = serializers.CharField(default="\n\n")
    chunk_size = serializers.IntegerField(default=1000)
    chunk_overlap = serializers.IntegerField(default=200)
    length_function = serializers.CharField(default="len", required=False)
    is_separator_regex = serializers.BooleanField(default=False)


class CodeSplitterModelSerializer(serializers.Serializer):
    code_string = serializers.CharField()
    language = serializers.CharField()  # Adjust according to the Language enum
    chunk_size = serializers.IntegerField(default=100)
    chunk_overlap = serializers.IntegerField(default=20)


class MarkdownSplitterModelSerializer(serializers.Serializer):
    markdown_document = serializers.CharField()
    headers_to_split_on = serializers.ListField(
        child=serializers.ListField(
            child=serializers.CharField(), min_length=2, max_length=2
        ),
        required=False,
    )
    strip_headers = serializers.BooleanField(default=True)
    split_recursively = serializers.BooleanField(default=False)
    chunk_size = serializers.IntegerField(default=500)
    chunk_overlap = serializers.IntegerField(default=30)


class JSONSplitterModelSerializer(serializers.Serializer):
    json_data = serializers.CharField()
    chunk_size = serializers.IntegerField(default=300)
    min_chunk_size = serializers.IntegerField(default=100)
    split_lists = serializers.BooleanField(default=False)


class RecursiveCharacterSplitterModelSerializer(serializers.Serializer):
    text = serializers.CharField()
    chunk_size = serializers.IntegerField(default=100)
    chunk_overlap = serializers.IntegerField(default=20)
    is_separator_regex = serializers.BooleanField(default=False)
    separators = serializers.ListField(child=serializers.CharField(), required=False)


class SemanticChunkerModelSerializer(serializers.Serializer):
    text = serializers.CharField()
    breakpoint_threshold_type = serializers.ChoiceField(
        choices=["percentile", "standard_deviation", "interquartile"],
        default="percentile",
    )


class SplitByTokensModelSerializer(serializers.Serializer):
    text = serializers.CharField()
    encoding = serializers.CharField(default="cl100k_base", required=False)
    encoding_name = serializers.CharField(default="gpt2", required=False)
    chunk_size = serializers.IntegerField(default=100)
    chunk_overlap = serializers.IntegerField(default=0)


class SplitDocumentRequestSerializer(serializers.Serializer):
    html_header_splitter = HTMLHeaderSplitterModelSerializer(required=False)
    html_section_splitter = HTMLSectionSplitterModelSerializer(required=False)
    character_splitter = CharacterSplitterModelSerializer(required=False)
    code_splitter = CodeSplitterModelSerializer(required=False)
    markdown_splitter = MarkdownSplitterModelSerializer(required=False)
    json_splitter = JSONSplitterModelSerializer(required=False)
    recursive_character_splitter = RecursiveCharacterSplitterModelSerializer(
        required=False
    )
    semantic_chunker = SemanticChunkerModelSerializer(required=False)
    split_by_tokens = SplitByTokensModelSerializer(required=False)

    def validate(self, data):
        if len(data) != 1:
            raise serializers.ValidationError(
                "Only one splitter type should be specified."
            )
        return data


class HTMLHeaderSplitterModel(BaseModel):
    html_string: str
    headers_to_split_on: Optional[List[Tuple[str, str]]] = Field(
        default=None, example=[("h1", "Header 1"), ("h2", "Header 2")]
    )
    split_recursively: bool = False
    chunk_size: int = 500
    chunk_overlap: int = 30


class HTMLSectionSplitterModel(BaseModel):
    html_string: str
    headers_to_split_on: Optional[List[Tuple[str, str]]] = Field(
        default=None, example=[("h1", "Header 1"), ("h2", "Header 2")]
    )
    split_recursively: bool = False
    chunk_size: int = 500
    chunk_overlap: int = 30


class CharacterSplitterModel(BaseModel):
    text: str
    separator: str = "\n\n"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    length_function: Optional[Callable[[str], int]] = len
    is_separator_regex: bool = False


class CodeSplitterModel(BaseModel):
    code_string: str
    language: Language
    chunk_size: int = 100
    chunk_overlap: int = 20


class MarkdownSplitterModel(BaseModel):
    markdown_document: str
    headers_to_split_on: Optional[List[Tuple[str, str]]] = Field(
        default=None, example=[("#", "Header 1"), ("##", "Header 2")]
    )
    strip_headers: bool = True
    split_recursively: bool = False
    chunk_size: int = 500
    chunk_overlap: int = 30


class JSONSplitterModel(BaseModel):
    json_data: str
    chunk_size: int = 300
    min_chunk_size: int = 100
    split_lists: bool = False


class RecursiveCharacterSplitterModel(BaseModel):
    text: str
    chunk_size: int = 100
    chunk_overlap: int = 20
    is_separator_regex: bool = False
    separators: Optional[List[str]] = Field(default=None, example=["\n\n", "\n", " "])


class SemanticChunkerModel(BaseModel):
    text: str
    breakpoint_threshold_type: Literal[
        "percentile", "standard_deviation", "interquartile"
    ] = "percentile"
    embedding_model: Optional[OpenAIEmbeddings] = None


class SplitByTokensModel(BaseModel):
    text: str
    encoding: Optional[str] = "cl100k_base"
    encoding_name: Optional[str] = "gpt2"
    chunk_size: int = 100
    chunk_overlap: int = 0


class Splitters:
    def html_header_splitter(self, model: HTMLHeaderSplitterModel) -> List[str]:
        splitter = HTMLHeaderTextSplitter(
            headers_to_split_on=model.headers_to_split_on
            or [
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
                ("h4", "Header 4"),
                ("h5", "Header 5"),
                ("h6", "Header 6"),
            ],
            split_recursively=model.split_recursively,
        )
        split_texts = splitter.split_text(model.html_string)
        return split_texts

    def html_section_splitter(self, model: HTMLSectionSplitterModel) -> List[str]:
        splitter = HTMLSectionSplitter(
            headers_to_split_on=model.headers_to_split_on
            or [
                ("h1", "Header 1"),
                ("h2", "Header 2"),
                ("h3", "Header 3"),
                ("h4", "Header 4"),
                ("h5", "Header 5"),
                ("h6", "Header 6"),
            ],
            split_recursively=model.split_recursively,
        )
        split_texts = splitter.split_text(model.html_string)
        return split_texts

    def character_splitter(self, model: CharacterSplitterModel) -> List[str]:
        text_splitter = CharacterTextSplitter(
            separator=model.separator,
            chunk_size=model.chunk_size,
            chunk_overlap=model.chunk_overlap,
            length_function=model.length_function,
            is_separator_regex=model.is_separator_regex,
        )
        split_texts = text_splitter.split_text(model.text)
        return split_texts

    def code_splitter(self, model: CodeSplitterModel) -> List[str]:
        code_splitter = RecursiveCharacterTextSplitter.from_language(
            language=model.language,
            chunk_size=model.chunk_size,
            chunk_overlap=model.chunk_overlap,
        )
        split_texts = code_splitter.split_text(model.code_string)
        return split_texts

    def markdown_splitter(self, model: MarkdownSplitterModel) -> List[str]:
        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=model.headers_to_split_on
            or [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
                ("####", "Header 4"),
                ("#####", "Header 5"),
            ],
            strip_headers=model.strip_headers,
        )
        md_header_splits = splitter.split_text(model.markdown_document)
        if model.split_recursively:
            split_texts = self.__recursive_text_splitter(
                text=model.markdown_document,
                chunk_size=model.chunk_size,
                chunk_overlap=model.chunk_overlap,
                is_separator_regex=False,
                separators=None,
            )
        else:
            split_texts = md_header_splits
        return split_texts

    def json_splitter(self, model: JSONSplitterModel) -> List[str]:
        splitter = RecursiveJsonSplitter(
            chunk_size=model.chunk_size, min_chunk_size=model.min_chunk_size
        )
        texts = splitter.split_text(
            json_data=model.json_data, convert_lists=model.split_lists
        )
        return texts

    def recursive_character_splitter(
        self, model: RecursiveCharacterSplitterModel
    ) -> List[str]:
        split_texts = self.__recursive_text_splitter(
            text=model.text,
            chunk_size=model.chunk_size,
            chunk_overlap=model.chunk_overlap,
            is_separator_regex=model.is_separator_regex,
            separators=model.separators,
        )
        return split_texts

    def semantic_chunker(self, model: SemanticChunkerModel) -> List[str]:
        if model.embedding_model is None:
            model.embedding_model = OpenAIEmbeddings()
        text_splitter = SemanticChunker(
            model.embedding_model,
            breakpoint_threshold_type=model.breakpoint_threshold_type,
        )
        split_texts = text_splitter.split_text(model.text)
        return split_texts

    def split_by_tokens(self, model: SplitByTokensModel) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding=model.encoding,
            encoding_name=model.encoding_name,
            chunk_size=model.chunk_size,
            chunk_overlap=model.chunk_overlap,
        )
        split_texts = text_splitter.split_text(model.text)
        return split_texts

    def __recursive_text_splitter(
        self,
        text: str,
        chunk_size: int,
        chunk_overlap: int,
        is_separator_regex: bool,
        separators: Optional[List[str]],
    ) -> List[str]:
        if separators is None:
            separators = ["\n\n", "\n", " ", ""]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            is_separator_regex=is_separator_regex,
            separators=separators,
        )
        return text_splitter.split_text(text)


def split_document(
    method: str,
    props: Union[
        HTMLHeaderSplitterModel,
        HTMLSectionSplitterModel,
        CharacterSplitterModel,
        CodeSplitterModel,
        MarkdownSplitterModel,
        JSONSplitterModel,
        RecursiveCharacterSplitterModel,
        SemanticChunkerModel,
        SplitByTokensModel,
    ],
) -> List[str]:
    splitters = Splitters()
    method_mapping = {
        "html_header_splitter": splitters.html_header_splitter,
        "html_section_splitter": splitters.html_section_splitter,
        "character_splitter": splitters.character_splitter,
        "code_splitter": splitters.code_splitter,
        "markdown_splitter": splitters.markdown_splitter,
        "json_splitter": splitters.json_splitter,
        "recursive_character_splitter": splitters.recursive_character_splitter,
        "semantic_chunker": splitters.semantic_chunker,
        "split_by_tokens": splitters.split_by_tokens,
    }
    if method in method_mapping:
        return method_mapping[method](props)
    else:
        raise ValueError(f"Method {method} is not supported.")
