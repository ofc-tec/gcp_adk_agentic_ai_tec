
from google.cloud import geminidataanalytics
from google.api_core.client_options import ClientOptions

# --------------------------------------------------
# Configuration
# --------------------------------------------------

PROJECT_ID = "ia-2006"
LOCATION = "us"

DATA_AGENT = (
    "projects/ia-2006/locations/us/dataAgents/"
    "agent_dff957ca-0fab-4a5d-81a7-f3cc17d2a1e1"
)

API_ENDPOINT = "geminidataanalytics.us.rep.googleapis.com"

# --------------------------------------------------
# Connect to our existing Data Agent
# --------------------------------------------------

client = geminidataanalytics.DataChatServiceClient(
    client_options=ClientOptions(
        api_endpoint=API_ENDPOINT
    )
)

# --------------------------------------------------
# Ask a question
# --------------------------------------------------

question = "How many flights are recorded in the dataset?"

message = geminidataanalytics.Message()
message.user_message.text = question

context = geminidataanalytics.DataAgentContext()
context.data_agent = DATA_AGENT

request = geminidataanalytics.ChatRequest(
    parent=f"projects/{PROJECT_ID}/locations/{LOCATION}",
    messages=[message],
    data_agent_context=context,
)

print(f"Question: {question}\n")

# --------------------------------------------------
# Process response
# --------------------------------------------------

for response in client.chat(request=request, timeout=300):

    if not response.system_message:
        continue

    system = response.system_message

    # Natural language response
    if system.text:
        if system.text.text_type == (
            geminidataanalytics.TextMessage.TextType.FINAL_RESPONSE
        ):
            print("\nANSWER:")
            print("\n".join(system.text.parts))

    # Generated SQL
    if system.data:
        if system.data.generated_sql:
            print("\nGENERATED SQL:")
            print(system.data.generated_sql)

print("\nDone.")
