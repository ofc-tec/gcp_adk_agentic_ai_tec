from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from data_agent.agent import root_agent as data_agent
from governance_rag.agent import root_agent as governance_agent

root_agent = Agent(
    name="data_steward_maestro",
    model="gemini-3.5-flash",

    instruction="""
    You are a Data Steward orchestrator.

    Delegate analytical questions to data_agent.
    Delegate governance questions to governance_rag.

    For questions requiring both, consult both agents.
    Never invent data or policies.
    """,

    tools=[
        AgentTool(agent=data_agent),
        AgentTool(agent=governance_agent),
    ],
)