"""
Governance RAG Agent
Google ADK + Google Cloud RAG Engine

Gemini inference: Gemini Developer API
Document retrieval: Google Cloud RAG Engine
"""

import os

# Disable Vertex AI for Gemini inference.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"


from google.adk.agents import Agent
import vertexai
from vertexai.preview import rag


PROJECT_ID = "ia-2006"
MODEL_ID = "gemini-3.5-flash"
RAG_REGION = "us-central1"

CORPUS = (
    "projects/ia-2006/locations/us-central1/"
    "ragCorpora/5553294582315220992"
)


# Initialize RAG Engine only.
vertexai.init(
    project=PROJECT_ID,
    location=RAG_REGION,
)


def retrieve_governance_documents(question: str) -> str:
    """Retrieve relevant governance policies from RAG Engine.

    Args:
        question: A question about organizational data governance policies.

    Returns:
        Relevant document passages with source information.
    """

    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(rag_corpus=CORPUS)
        ],
        text=question,
        rag_retrieval_config=rag.RagRetrievalConfig(
            top_k=3
        ),
    )

    contexts = (
        response.contexts.contexts
        if response.contexts else []
    )

    if not contexts:
        return "No relevant governance documents found."

    return "\n\n".join(
        f"Source: {context.source_uri}\n"
        f"Content: {context.text}"
        for context in contexts
    )


root_agent = Agent(
    name="governance_rag",

    model=MODEL_ID,

    description=(
        "Specialist in organizational data governance policies. "
        "Answers policy questions using Google RAG Engine."
    ),

    instruction="""
You are a Data Governance specialist.

Use retrieve_governance_documents to answer questions
about organizational governance policies.

INSTRUCTIONS:
1. Retrieve relevant documents before answering.
2. Base answers exclusively on retrieved passages.
3. Cite source documents when available.
4. Never invent policy requirements.
5. If documentation is insufficient, say so.
6. Do not call the retrieval tool multiple times.

Answer clearly and concisely.
""",

    tools=[retrieve_governance_documents],
)