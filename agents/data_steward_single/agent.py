"""
Single-Agent Data Steward — Google ADK

Three tool sources:
1. BigQuery Conversational Analytics Data Agent
2. Vertex AI Governance RAG
3. Google-managed BigQuery MCP server

Run:
    cd ~/data_steward
    uv run adk web agents
"""

import google.auth
from google.auth.transport.requests import Request

from google.adk.agents import Agent

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

from .data_agent.agent import (
    root_agent as data_agent,
    DATA_AGENT,
)

from .governance_rag.agent import (
    root_agent as governance_agent,
)


# --------------------------------------------------
# Google Cloud configuration
# --------------------------------------------------

PROJECT_ID = "ia-2006"

BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"


# --------------------------------------------------
# Google Cloud authentication
# --------------------------------------------------

credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def get_mcp_headers(context=None):
    """
    Generate authentication headers for Google MCP.

    Refresh the access token when necessary.
    """
    if not credentials.valid:
        credentials.refresh(Request())

    return {
        "Authorization": f"Bearer {credentials.token}"
    }


# --------------------------------------------------
# BigQuery MCP Toolset
# --------------------------------------------------

bigquery_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=BIGQUERY_MCP_URL,
        timeout=30,
        sse_read_timeout=300,
    ),
    header_provider=get_mcp_headers,
)


# --------------------------------------------------
# Single ADK Agent
# --------------------------------------------------

root_agent = Agent(
    name="data_steward_single",

    model="gemini-3.5-flash",

    description=(
        "Single Data Steward agent combining BigQuery "
        "Conversational Analytics, Governance RAG, "
        "and Google BigQuery MCP tools."
    ),

    instruction=f"""
You are an enterprise Data Steward.

You have access to three tool sources.

--------------------------------------------------
1. BIGQUERY CONVERSATIONAL ANALYTICS
--------------------------------------------------

Tool: ask_data_agent

Existing Data Agent resource:

{DATA_AGENT}

Use this tool to answer analytical questions about:
- Airlines
- Flight delays
- Cancellations
- Statistical summaries
- Data quality

Always provide the exact Data Agent resource when
calling ask_data_agent.

Never invent numerical results.


--------------------------------------------------
2. GOVERNANCE RAG
--------------------------------------------------

Tool: retrieve_governance_documents

Use this tool for:
- Data ownership
- Data classification
- Retention policies
- Privacy
- Organizational governance requirements

Base governance claims on retrieved documents.

Do not invent policies.


--------------------------------------------------
3. BIGQUERY MCP
--------------------------------------------------

You also have access to tools from Google's
managed BigQuery MCP server.

Use these tools for:
- Discovering datasets
- Listing tables
- Inspecting table schemas
- Exploring metadata
- Executing read-only SQL when appropriate

The Google Cloud project is:

{PROJECT_ID}

Never modify or delete data.

Do not assume that datasets or tables exist
without checking.


--------------------------------------------------
TOOL SELECTION
--------------------------------------------------

For analytical questions:
Prefer ask_data_agent.

For dataset discovery and metadata exploration:
Prefer BigQuery MCP tools.

For governance questions:
Use retrieve_governance_documents.

For questions requiring multiple capabilities:
Use the relevant tools and combine their findings.

Never invent tool results.

If a tool fails, report the limitation.
Do not automatically retry failed calls.

Keep answers clear and concise.
""",

    tools=[
        *data_agent.tools,
        *governance_agent.tools,
        bigquery_mcp,
    ],
)