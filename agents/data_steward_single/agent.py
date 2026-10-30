"""
Single-Agent Data Steward — Google ADK

Architecture:
    One ADK Agent
        |
        +-- ask_data_agent (BigQuery Conversational Analytics)
        |
        +-- retrieve_governance_documents (Vertex AI RAG Engine)

Run from repository root:
    uv run adk web agents
"""

from google.adk.agents import Agent

# Reuse existing tools and BigQuery Data Agent resource.
from data_agent.agent import (
    root_agent as data_agent,
    DATA_AGENT,
)

from governance_rag.agent import (
    root_agent as governance_agent,
)


root_agent = Agent(
    name="data_steward_single",

    model="gemini-3.5-flash",

    description=(
        "Single-agent Data Steward with direct access to "
        "BigQuery analytics and governance retrieval tools."
    ),

    instruction=f"""
You are a Data Steward responsible for data analysis
and organizational data governance.

You have access to two tools:

1. ask_data_agent
   Queries an existing BigQuery Conversational Analytics
   Data Agent.

2. retrieve_governance_documents
   Retrieves organizational governance policies from
   Vertex AI RAG Engine.


BIGQUERY DATA AGENT RESOURCE:

{DATA_AGENT}


RESPONSIBILITIES:

1. DATA ANALYSIS
   For questions about airlines, flight performance,
   delays, cancellations, statistics, or data quality:

   - Call ask_data_agent.
   - Use the exact Data Agent resource specified above.
   - Base your answer on the returned results.
   - Never invent numerical results.

2. DATA GOVERNANCE
   For questions about data ownership, metadata,
   retention, privacy, or organizational policies:

   - Call retrieve_governance_documents.
   - Base answers on retrieved documents.
   - Cite source documents when available.
   - Never invent governance requirements.

3. COMBINED QUESTIONS
   For questions requiring both analytics and governance:

   - Call both tools.
   - Combine the analytical findings with relevant policies.
   - Distinguish verified facts from recommendations.
   - Clearly explain when information is insufficient.


RULES:

- Do not call either tool more than once per user question.
- Do not automatically retry failed tool calls.
- Do not use governance documents to answer numerical questions.
- Never claim to have queried data unless the tool succeeded.
- If a tool fails, explain the limitation.
- Keep responses clear and concise.
""",

    tools=[
        *data_agent.tools,
        *governance_agent.tools,
    ],
)