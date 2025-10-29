import vertexai
from vertexai import agent_engines
from config import config

# Initialize Vertex AI
vertexai.init(
    project=config.GOOGLE_CLOUD_PROJECT,
    location=config.GOOGLE_CLOUD_LOCATION
)

# Get the deployed agent engine
agent_engine = agent_engines.get(
    'projects/519243981219/locations/us-central1/reasoningEngines/8395400198720847872'
)

# Test queries
test_queries = [
    "Hello! What can you help me with?",
    "Show me trains from Delhi to Mumbai",
    "Check seat availability for train 12806",
    "What's the status of train 12760?",
    "Find station code for Hyderabad"
]

print("🚂 Testing Indian Railway Assistant Agent Engine")
print("=" * 50)

def _extract_from_dict_event(event: dict) -> str:
    """Extract text from dictionary-style events (AgentEngine format)."""
    # Handle AgentEngine response format
    if "parts" in event and "role" in event:
        # Only extract text from model responses, skip function calls/responses
        if event.get("role") == "model":
            parts = event.get("parts", [])
            text_parts = []

            for part in parts:
                # Extract text content, skip function calls
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])

            return "".join(text_parts) if text_parts else None
        return None

    # Handle other dict formats
    content = event.get("content", {})
    if isinstance(content, str):
        return content

    parts = content.get("parts", [])
    if not parts:
        return None

    text_parts = []
    for part in parts:
        if isinstance(part, dict) and "text" in part:
            text_parts.append(part["text"])

    return "".join(text_parts) if text_parts else None

for i, query in enumerate(test_queries, 1):
    print(f"\n{i}. Query: {query}")
    print("-" * 30)
    
    try:
        # Send query to agent using the correct method
        response_stream = agent_engine.stream_query(message=query,)
        
        # Collect the streaming response
        full_response = ""
        for chunk in response_stream:
            if hasattr(chunk, 'text') and chunk.text:
                full_response += chunk.text
            elif isinstance(chunk, str):
                full_response += chunk
        
        print(f"Response: {full_response}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()

print("✅ Testing completed!")
