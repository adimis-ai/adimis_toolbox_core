import os
from pathlib import Path
from langchain.schema import Document
from rest_framework import serializers
from typing import List, Literal, Union
from django.core.files.uploadedfile import UploadedFile
from langchain_community.document_loaders import (
    TextLoader,
    JSONLoader,
    PyPDFLoader,
    CSVLoader,
    UnstructuredXMLLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    SeleniumURLLoader,
    PlaywrightURLLoader,
    UnstructuredURLLoader,
    WebBaseLoader,
)


class UrlsLoaderPropsSerializer(serializers.Serializer):
    urls = serializers.ListField(child=serializers.URLField(), allow_empty=False)
    loader_type = serializers.ChoiceField(
        choices=["unstructured", "selenium", "playwright", "web_html"]
    )
    loader_kwargs = serializers.DictField(child=serializers.CharField(), required=False)


class UploadedFilesLoaderPropsSerializer(serializers.Serializer):
    files = serializers.ListField(child=serializers.FileField(), allow_empty=False)


class LoadDocumentsRequestSerializer(serializers.Serializer):
    method = serializers.ChoiceField(choices=["urls", "uploaded_files"])
    url_loader_props = UrlsLoaderPropsSerializer(required=False)
    upload_file_loader_props = UploadedFilesLoaderPropsSerializer(required=False)

    def validate(self, data):
        method = data.get("method")
        if method == "urls" and "url_loader_props" not in data:
            raise serializers.ValidationError(
                "url_loader_props is required when method is 'urls'"
            )
        if method == "uploaded_files" and "upload_file_loader_props" not in data:
            raise serializers.ValidationError(
                "upload_file_loader_props is required when method is 'uploaded_files'"
            )
        return data


class UrlsLoaderProps:
    def __init__(
        self,
        urls: List[str],
        loader_type: Literal["unstructured", "selenium", "playwright", "web_html"],
        **loader_kwargs,
    ):
        self.urls = urls
        self.loader_type = loader_type
        self.loader_kwargs = loader_kwargs


class UploadedFilesLoaderProps:
    def __init__(self, files: List[UploadedFile]):
        self.files = files


class UrlsLoader:
    def __init__(self, props: UrlsLoaderProps):
        self.urls = props.urls
        self.loader_type = props.loader_type
        self.loader_kwargs = props.loader_kwargs

    def __update_metadata_with_url(
        self, documents: List[Document], url: str
    ) -> List[Document]:
        for doc in documents:
            doc.metadata["url"] = url
        return documents

    def load(self) -> List[Document]:
        all_documents = []

        for url in self.urls:
            if self.loader_type == "unstructured":
                loader = UnstructuredURLLoader(urls=[url], **self.loader_kwargs)
            elif self.loader_type == "selenium":
                loader = SeleniumURLLoader(urls=[url], **self.loader_kwargs)
            elif self.loader_type == "playwright":
                loader = PlaywrightURLLoader(urls=[url], **self.loader_kwargs)
            elif self.loader_type == "web_html":
                loader = WebBaseLoader([url], **self.loader_kwargs)
            else:
                raise ValueError(f"Unsupported loader type: {self.loader_type}")

            documents = loader.load()
            documents = self.__update_metadata_with_url(documents, url)
            all_documents.extend(documents)

        return all_documents


class UploadedFilesLoader:
    def __init__(self, props: UploadedFilesLoaderProps):
        self.__files = props.files

    def __save_temp_file(self, uploaded_file: UploadedFile) -> str:
        temp_file_path = f"/tmp/{uploaded_file.name}"
        with open(temp_file_path, "wb") as temp_file:
            for chunk in uploaded_file.chunks():
                temp_file.write(chunk)
        return temp_file_path

    def __cleanup_temp_file(self, file_path: str):
        try:
            os.remove(file_path)
        except OSError:
            pass

    def __update_metadata_with_filename(
        self, documents: List[Document], filename: str
    ) -> List[Document]:
        for doc in documents:
            doc.metadata["filename"] = filename
        return documents

    def __load_text(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = TextLoader(file_path)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_json(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = JSONLoader(file_path, jq_schema=".", text_content=False)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_pdf(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = PyPDFLoader(file_path)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_csv(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = CSVLoader(file_path)
        documents = list(loader.load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_xml(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = UnstructuredXMLLoader(file_path)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_html(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = UnstructuredHTMLLoader(file_path)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def __load_markdown(self, uploaded_file: UploadedFile) -> List[Document]:
        file_path = self.__save_temp_file(uploaded_file)
        loader = UnstructuredMarkdownLoader(file_path)
        documents = list(loader.lazy_load())
        self.__cleanup_temp_file(file_path)
        return self.__update_metadata_with_filename(documents, uploaded_file.name)

    def load(self) -> List[Document]:
        documents = []
        for uploaded_file in self.__files:
            file_extension = Path(uploaded_file.name).suffix.lower()

            if file_extension == ".txt":
                docs = self.__load_text(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".json":
                docs = self.__load_json(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".pdf":
                docs = self.__load_pdf(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".csv":
                docs = self.__load_csv(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".xml":
                docs = self.__load_xml(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".html" or file_extension == ".htm":
                docs = self.__load_html(uploaded_file)
                documents.extend(docs)
            elif file_extension == ".md":
                docs = self.__load_markdown(uploaded_file)
                documents.extend(docs)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

        return documents


def create_loader(
    method: Literal["urls", "uploaded_files"],
    schema: Union[UrlsLoaderProps, UploadedFilesLoaderProps],
) -> Union[UrlsLoader, UploadedFilesLoader]:
    if method == "urls":
        if isinstance(schema, UrlsLoaderProps):
            return UrlsLoader(schema)
        else:
            raise ValueError("Invalid schema for UrlsLoader")
    elif method == "uploaded_files":
        if isinstance(schema, UploadedFilesLoaderProps):
            return UploadedFilesLoader(schema)
        else:
            raise ValueError("Invalid schema for UploadedFilesLoader")
