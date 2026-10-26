"""
BigQuery Data Analyst — ADK Agent

Uses Google's native DataAgentToolset to connect to our
existing BigQuery Conversational Analytics Data Agent.

Run:
    cd ~/data_steward
    adk web agents
"""

import os
import google.auth

from google.adk.agents import Agent
from google.adk.tools.data_agent import (
    DataAgentToolset,
    DataAgentCredentialsConfig,
)
from google.adk.tools.data_agent.config import DataAgentToolConfig


# --------------------------------------------------
# Google Cloud configuration
# --------------------------------------------------

PROJECT_ID = "ia-2006"

DATA_AGENT = (
    "projects/ia-2006/locations/us/dataAgents/"
    "agent_dff957ca-0fab-4a5d-81a7-f3cc17d2a1e1"
)

API_ENDPOINT = "geminidataanalytics.us.rep.googleapis.com"

# Gemini uses Vertex AI authentication.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


# --------------------------------------------------
# Google Cloud credentials
# --------------------------------------------------

credentials, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


# --------------------------------------------------
# Native BigQuery Data Agent toolset
# --------------------------------------------------

data_agent_toolset = DataAgentToolset(
    credentials_config=DataAgentCredentialsConfig(
        credentials=credentials
    ),
    data_agent_tool_config=DataAgentToolConfig(
        location="us",
        max_query_result_rows=20,        
    ),
    tool_filter=["ask_data_agent"],
)


# --------------------------------------------------
# ADK Agent
# --------------------------------------------------

root_agent = Agent(
    name="data_agent",

    model="gemini-3.8-flash",

    description=(
        "BigQuery flight data analyst using an existing "
        "Google Cloud Conversational Analytics Data Agent."
    ),

    instruction=f"""
You are a BigQuery Data Analyst specializing in airline flight data.

You have access to an existing Google Cloud Data Agent through
the ask_data_agent tool.

DATA AGENT RESOURCE:
{DATA_AGENT}

YOUR RESPONSIBILITIES:

1. Answer questions about airline flight performance, delays,
   cancellations, airports, and airlines.

2. Use ask_data_agent for analytical questions requiring
   information from BigQuery.

3. Always use the Data Agent resource specified above.

4. Base your answers on the results returned by the Data Agent.

RULES:

- Call ask_data_agent at most once per user question.
- Do not invent SQL queries, statistics, or numerical results.
- Do not independently reinterpret unsupported query results.
- If the Data Agent cannot answer, explain the limitation.
- Do not automatically retry failed tool calls.
- Include the generated SQL when it is available and useful.

Your role is to provide a natural-language interface to the
existing BigQuery Data Agent.
""",

    tools=[data_agent_toolset],
)