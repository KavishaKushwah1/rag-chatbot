"""
Ragas needs a LangChain-wrapped LLM + embeddings to act as judge for
faithfulness/relevancy/precision/recall scoring. We reuse the same
Gemini credentials already configured for the app, rather than adding
a separate provider just for eval.
"""
from __future__ import annotations
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from app.config import settings


def get_ragas_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=settings.gemini_api_key,
        temperature=0.0,
    )
    return LangchainLLMWrapper(llm)


def get_ragas_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=settings.gemini_api_key,
    )
    return LangchainEmbeddingsWrapper(embeddings)