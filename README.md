# Google ADK Agentic AI — Tec de Monterrey

Two educational **Google Agent Development Kit (ADK)** agents that integrate with Google Cloud data and retrieval services. This repository supports teaching agent tools, RAG, orchestration, and evaluation.

> **Current state:** Two independent agents are implemented. A combined orchestrator, MCP/A2A server, Agent Registry registration, and automated evaluations are **not yet included**.

## Architecture

```text
                  ADK web / ADK CLI
                         |
               +---------+----------+
               |                    |
       agents/data_agent    agents/governance_rag
               |                    |
        DataAgentToolset    Python retrieval tool
               |                    |
    Conversational Analytics    Vertex AI RAG Engine
        (existing Data Agent)     (existing RAG corpus)
               |
            BigQuery
```

Both folders expose a `root_agent` following ADK conventions. They are not yet connected to a shared orchestrator.

## Repository layout

```text
agents/
├── data_agent/
│   ├── __init__.py
│   └── agent.py
└── governance_rag/
    ├── __init__.py
    └── agent.py
```

The `governance_rag` directory also contains files marked as backups/deprecated experiments; these are not supported entry points.

## Implemented agents

### 1. BigQuery Data Analyst (`agents/data_agent/agent.py`)

An airline flight-data analyst that calls an **existing BigQuery Conversational Analytics Data Agent** through ADK's `DataAgentToolset`.

- Cloud project: `ia-2006`
- Data Agent resource location: `us`
- Endpoint configured in code: `geminidataanalytics.us.rep.googleapis.com`
- Exposed tool: `ask_data_agent`
- Maximum query result rows configured: `20`
- Agent is instructed to call the tool at most once per question and include generated SQL when available and useful.

Example prompts:

- Which airlines have the longest average arrival delays?
- How many flights were cancelled by airline?
- Show the SQL used to answer that question.

**Note:** The agent references an existing cloud Data Agent. This repository does not create that Data Agent or load data into BigQuery.

### 2. Governance RAG (`agents/governance_rag/agent.py`)

A data-governance specialist using the Python tool `retrieve_governance_documents(question: str)` and **Vertex AI RAG Engine**.

- Cloud project: `ia-2006`
- RAG region: `us-central1`
- Retrieval API: `vertexai.preview.rag.retrieval_query`
- Retrieval configuration: `top_k=3`
- Results include source URIs and document passages.
- Agent instructions require answers grounded in retrieved passages and acknowledgement when evidence is missing.

Example prompts:

- What do our documented data retention policies require?
- What policies govern access to sensitive records?
- Is there documented support for sharing this dataset?

**Note:** The RAG corpus must already exist and contain indexed documents; this repository does not ingest or provision the corpus.

## Getting started

### Prerequisites

- Python and `gcloud` CLI.
- Access to project `ia-2006` and permission to invoke the existing Data Agent and RAG corpus.
- Google Cloud Application Default Credentials for service calls.
- Gemini inference credentials for the model backend selected in the source code.

Clone and set up an environment:

```bash
git clone https://github.com/ofc-tec/gcp_adk_agentic_ai_tec.git
cd gcp_adk_agentic_ai_tec
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade google-adk google-cloud-aiplatform google-auth

gcloud auth application-default login
gcloud config set project ia-2006
```

There is **no pinned requirements file** in the repository yet. The installation command is a starting point; compatible package versions may depend on current ADK APIs.

### Check model configuration

The current source files specify:

| Agent | Model ID in source |
| --- | --- |
| `data_agent` | `gemini-3.8-flash` |
| `governance_rag` | `gemini-3.5-flash` |

**Verify these exact model IDs in your environment** and replace them if unavailable. Their availability has not been verified here.

Both files set `GOOGLE_GENAI_USE_VERTEXAI` to false for **Gemini inference**, which is separate from their use of Google Cloud data services. Configure an appropriate Gemini Developer API key (for example, via `GOOGLE_API_KEY`) if required by your ADK setup. Do not commit secrets.

### Run locally

From the repository root:

```bash
adk web agents
```

Open the localhost URL printed by ADK and choose `data_agent` or `governance_rag`.

Alternatively, run each agent separately:

```bash
adk run agents/data_agent
# or
adk run agents/governance_rag
```

The code exposes agents for the ADK runner; it does not implement a standalone CLI `main()`.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Model not found | Replace the model ID with one supported by the configured backend. |
| Authentication failure | Check Gemini credentials separately from `gcloud auth application-default login`. |
| Permission denied | Confirm project/region and permissions for the referenced cloud resources. |
| No RAG results | Confirm the corpus exists and contains relevant indexed policies. |
| Import error | Check ADK/Vertex AI SDK versions; some APIs are preview/evolving. |
| Data Agent fails | Verify its resource name, endpoint, location and underlying BigQuery access. |

## Next steps: orchestration, MCP, A2A, and Agent Registry

**None of these integration paths is implemented in the repository yet.**

| Pattern | Use case | Teaching value |
| --- | --- | --- |
| Native ADK `AgentTool` or sub-agents | Compose the two specialists in one Python app | Lowest-friction introduction to delegation |
| MCP | Expose tools/functions to MCP-compatible consumers | Tool interoperability |
| A2A | Delegate tasks to independently hosted agents | Agent-to-agent interoperability |
| Agent Registry | Discover registered/deployed agent endpoints and capabilities | Distributed agent discovery |
| Evaluation | Test task success, tool use and groundedness | Reliability and reproducibility |

**Recommended progression:** start with **native ADK orchestration**, then demonstrate **A2A** for remotely hosted specialists. Use **MCP** when a capability is best exposed as a reusable tool. An agent is **not** automatically registered/discoverable merely because its Python code is in GitHub or calls managed Google Cloud services.

### Domain alignment

The implemented `data_agent` specializes in **airline flight data**. The governance agent answers from **whatever governance documents are indexed in its RAG corpus**. Do not assume these domains align automatically. For the course's banking Data Steward challenge, adapt the analytical data source or clearly frame the combined demo as a flight-data governance example.

## Suggested evaluation cases

Build a small test set and record:

1. **Task success:** Did the agent complete the user request?
2. **Tool selection:** Did it choose and call the appropriate tool?
3. **Groundedness:** Are numeric and policy claims supported by tool results?
4. **Unsupported requests:** Does it admit insufficient evidence instead of inventing facts?
5. **Efficiency:** What were the number of calls, latency and token usage?

Test at least one valid analytical query, one documented governance question, one question absent from the corpus, and one request beyond the agent's permissions. A plausible answer alone is not evidence of correctness.

## Security and limitations

These are **instructional examples**, not production-ready governance enforcement systems.

- Prefer synthetic/approved datasets; never commit API keys or sensitive banking data.
- Tool-use instructions such as “call only once” are behavioral guidelines, **not** security controls.
- Review IAM permissions, audit logging, billing, quotas and data residency before deployment.
- Move hard-coded resource names, model IDs and project settings to environment configuration before reuse.

## References

- [Google Agent Development Kit](https://google.github.io/adk-docs/)
- [BigQuery](https://cloud.google.com/bigquery)
- [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Agent2Agent Protocol](https://a2a-protocol.org/)
