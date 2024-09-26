import openai
from typing import Union
from .types import LLMConfig
from langchain.chains.llm import LLMChain
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI


def get_openai_models(api_key: str) -> list:
    try:
        print("Calling get_openai_models...")
        openai.api_key = api_key
        client = openai.OpenAI()
        response = client.models.list()
        model_names = [model.id for model in response.data if "gpt" in model.id]
        models = [
            {"id": model, "label": model, "value": model} for model in model_names
        ]
        print("model names: {}".format(models))
        return models
    except Exception as e:
        print(f"Error fetching OpenAI models: {e}")
        return []


class LLMRegistry:
    @classmethod
    def get_openai_llm(cls, llm_config: LLMConfig) -> OpenAI:
        return OpenAI(
            model=llm_config.llm_model_name,
            temperature=llm_config.temperature,
            api_key=llm_config.api_key,
            request_timeout=llm_config.timeout,
            max_retries=llm_config.max_retries,
            max_tokens=llm_config.max_tokens,
            n=llm_config.n,
            streaming=True,
        )

    @classmethod
    def get_openai_chat_llm(cls, llm_config: LLMConfig) -> ChatOpenAI:
        return ChatOpenAI(
            model=llm_config.llm_model_name,
            temperature=llm_config.temperature,
            api_key=llm_config.api_key,
            request_timeout=llm_config.timeout,
            max_retries=llm_config.max_retries,
            max_tokens=llm_config.max_tokens,
            n=llm_config.n,
            streaming=True,
        )

    @classmethod
    def get_gemini_llm(cls, llm_config: LLMConfig) -> GoogleGenerativeAI:
        return GoogleGenerativeAI(
            model=llm_config.llm_model_name,
            temperature=llm_config.temperature,
            google_api_key=llm_config.api_key,
            request_timeout=llm_config.timeout,
            max_retries=llm_config.max_retries,
            max_tokens=llm_config.max_tokens,
            n=llm_config.n,
            top_p=llm_config.top_p,
        )

    @classmethod
    def get_gemini_chat_llm(cls, llm_config: LLMConfig) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=llm_config.llm_model_name,
            temperature=llm_config.temperature,
            google_api_key=llm_config.api_key,
            request_timeout=llm_config.timeout,
            max_retries=llm_config.max_retries,
            max_tokens=llm_config.max_tokens,
            n=llm_config.n,
            top_p=llm_config.top_p,
        )

    @classmethod
    def instance(
        cls, llm_config: LLMConfig
    ) -> Union[ChatOpenAI, OpenAI, ChatGoogleGenerativeAI, GoogleGenerativeAI]:
        if llm_config.provider == "openai":
            return cls.get_openai_llm(llm_config=llm_config)
        elif llm_config.provider == "openai_chat":
            return cls.get_openai_chat_llm(llm_config=llm_config)
        elif llm_config.provider == "gemini":
            return cls.get_gemini_llm(llm_config=llm_config)
        elif llm_config.provider == "gemini_chat":
            return cls.get_gemini_chat_llm(llm_config=llm_config)

    @classmethod
    def chain(cls, system_prompt: str, llm_config: LLMConfig) -> LLMChain:
        if llm_config.provider in {"gemini_chat", "openai_chat"}:
            raise ValueError("Chat models cannot be used when the LLM is a tool")
        template = f"{system_prompt}\nQuery: {{query}}"
        prompt = PromptTemplate(input_variables=["query"], template=template)
        return LLMChain(
            llm=cls.instance(llm_config=llm_config),
            prompt=prompt,
        )
