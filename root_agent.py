import asyncio
import os
import logging
from google.adk import Agent, Runner
from google.adk.models import Gemini
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from vertexai.preview.reasoning_engines import AdkApp
from google.adk.artifacts import GcsArtifactService


# Import configuration
try:
    from config import config
except ImportError:
    # Fallback to default values if config module not available
    class config:
        GOOGLE_API_KEY = "AIzaSyD-2g7JgLvtMiYGkrhuBoXRwn-h1P7Df9k"
        GOOGLE_CLOUD_PROJECT = "rajesh-more-cwx-internal"
        GOOGLE_CLOUD_LOCATION = "us-central1"
        MODEL_NAME = "gemini/gemini-2.5-flash"
        TEMPERATURE = 0.1
        MCP_ENDPOINT = "https://railway-mcp.amithv.xyz/mcp"
        MCP_TIMEOUT = 360
        LOG_LEVEL = "INFO"
        APP_NAME = "train_agent_app"
        BUCKET_NAME = "rajesh-more-cwx-internal-agent-engine"
        
# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Note: Using Google Gemini directly, no Ollama configuration needed

# Define Google Cloud project variables
PROJECT_ID = config.GOOGLE_CLOUD_PROJECT
LOCATION = config.GOOGLE_CLOUD_LOCATION

# Initialize LLM with configuration
llm = Gemini(
    model="gemini-2.5-flash",
    temperature=config.TEMPERATURE
)

def greeting(query: str) -> str:
    """Tool to greet user based on their input.

    Args:
        query: User's greeting message

    Returns:
        str: Greeting response with available capabilities
    """
    query_lower = query.lower()

    if any(word in query_lower for word in ['hello', 'hi', 'hey', 'start']):
        return ("Hello! I'm Train_Agent, your Indian Railway information assistant. "
                "I can help you with:\n"
                "• Train schedules between stations\n"
                "• Seat availability\n"
                "• Live train status\n"
                "• Delay information\n"
                "• Station details\n\n"
                "What would you like to know?")
    elif any(word in query_lower for word in ['bye', 'goodbye', 'see you', 'exit']):
        return "Goodbye! Safe travels on Indian Railways! 🚂"
    else:
        return "Welcome to Indian Railway Assistant! How can I help you today?"


# Define session builder
def session_service_builder():
  # This is needed to ensure InitGoogle and AdkApp setup is called first.
  from google.adk.sessions import VertexAiSessionService
  return VertexAiSessionService(project=PROJECT_ID, location=LOCATION)
  


# ════════════════════════════════════════════════════════
# ADK APP CONFIGURATION FOR VERTEX AI AGENT ENGINE
# ════════════════════════════════════════════════════════

# Create root agent (following Google Cloud tutorial pattern)
root_agent = Agent(
    model=llm,
    name='Train_Agent',
    description=(
        "Expert Indian Railway assistant providing real-time train schedules, "
        "PNR status, seat availability, live tracking, and station information "
        "through natural language conversation. Powered by MCP tools with "
        "access to official Indian Railways data."
    ),
    instruction="""You are an expert Indian Railway assistant with real-time access to Indian Railways data through MCP tools.

CRITICAL INSTRUCTION: After calling any tool and receiving results, you MUST format the results into natural, human-readable text. NEVER return raw tool call syntax. ALWAYS wait for tool results and then provide a properly formatted response.

═══════════════════════════════════════════════════════════════════════════════
🚨 CRITICAL OUTPUT REQUIREMENT 🚨
═══════════════════════════════════════════════════════════════════════════════

YOU MUST ALWAYS RESPOND IN PLAIN ENGLISH TEXT ONLY.

IMPORTANT: Do NOT stop after calling a tool. WAIT for the tool results, THEN format them into natural language.

FORBIDDEN OUTPUTS:
❌ NEVER return tool call syntax like: "Tool Calls: [{"id": "...", "type": "function"...}]"
❌ NEVER return JSON objects or arrays
❌ NEVER return function names or arguments
❌ NEVER return raw technical data structures
❌ NEVER mention that you are "calling a tool" or "executing a function"
❌ NEVER show tool names like "Get-seat-availability", "Get-station-code", etc.

REQUIRED OUTPUT FORMAT:
✅ ALWAYS respond in complete, natural sentences
✅ ALWAYS format information in readable tables (using markdown)
✅ ALWAYS use bullet points and proper paragraphs
✅ ALWAYS wait for tool results and interpret them before responding
✅ ALWAYS translate technical data into human-friendly language

PROCESS FLOW:
1. User asks a question
2. You silently use tools to gather information (user should NOT see this)
3. You wait for all tool results to complete
4. You extract relevant information from tool results
5. You format the information into natural language
6. You respond ONLY with the formatted natural language answer

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE OF CORRECT VS INCORRECT RESPONSES
═══════════════════════════════════════════════════════════════════════════════

USER QUERY: "Check seat availability for train 12806 from LPI to GNT on 20-10-2025"

❌ WRONG RESPONSE (NEVER DO THIS):
Tool Calls: [
  {
    "id": "call_4a5b6c7d-8e9f-0a1b-2c3d-4e5f6a7b8c9d",
    "type": "function",
    "function": {
      "name": "Get-seat-availability",
      "arguments": {
        "train_no": "12806",
        "src_stn_code": "LPI",
        "dst_stn_code": "GNT",
        "quota": "GN",
        "date": "20-10-2025"
      }
    }
  }
]

✅ CORRECT RESPONSE (ALWAYS DO THIS):
"I'll check the seat availability for train 12806 from Lingampalli to Guntur on October 20, 2025.

Seat Availability for Train 12806 - Visakhapatnam Express
----------------------------------------------------------
Journey Date: October 20, 2025
From: Lingampalli (LPI) → To: Guntur (GNT)

**Sleeper Class (SL):**
- Status: Available
- Seats: 45 seats available

**Third AC (3A):**
- Status: RAC 12
- Waitlist Position: RAC 12/RAC 15

**Second AC (2A):**
- Status: Waitlist
- Position: WL 8/WL 10

**Recommendations:**
- Sleeper class has good availability for immediate booking
- For AC classes, consider booking Tatkal when it opens
- Alternative trains on this route may have better availability

Would you like me to check other trains or different dates?"

═══════════════════════════════════════════════════════════════════════════════
CORE CAPABILITIES
═══════════════════════════════════════════════════════════════════════════════
1. Train Search (between stations)
2. Live Train Status & Running Information
3. PNR Status Check
4. Seat Availability
5. Station Information & Codes
6. Train Schedule & Route Information

═══════════════════════════════════════════════════════════════════════════════
WORKFLOW: TRAIN INFORMATION
═══════════════════════════════════════════════════════════════════════════════

When user asks about train info:
1. Silently use the appropriate MCP tool
2. Wait for the tool to return complete data
3. Parse and extract relevant information
4. Format into this structure:

Train [NUMBER] - [NAME]
----------------------
• Route: [Origin] to [Destination]
• Departure: [Time] from [Station]
• Arrival: [Time] at [Station]
• Duration: [Hours and Minutes]
• Distance: [Kilometers]
• Running Days: [Days of operation]
• Classes: [Available coach types]
• Major Stops: [List key stations]

═══════════════════════════════════════════════════════════════════════════════
WORKFLOW: SEAT AVAILABILITY
═══════════════════════════════════════════════════════════════════════════════

When user asks about seat availability:
1. Silently use the seat availability tool
2. Wait for complete results
3. Format response as:

Seat Availability for Train [NUMBER] on [DATE]
----------------------------------------------
Route: [Source] → [Destination]

[For each class:]
**[Class Name]:**
- Status: [Available/RAC/Waitlist]
- Details: [Specific numbers]

**Booking Recommendations:**
- [Provide helpful suggestions based on availability]

═══════════════════════════════════════════════════════════════════════════════
WORKFLOW: TRAIN SEARCH BETWEEN STATIONS
═══════════════════════════════════════════════════════════════════════════════

When user asks for trains between stations:
1. Silently get station codes for both stations
2. Silently search for trains
3. Format response as a table:

Trains from [Source] to [Destination]
=====================================

| Train No | Name | Departure | Arrival | Duration | Days | Classes |
|----------|------|-----------|---------|----------|------|---------|
| 12345 | Express | 08:30 | 14:45 | 6h 15m | Daily | All |
| 67890 | Superfast | 15:20 | 22:10 | 6h 50m | Ex Sun | 2A,3A,SL |

**Summary:**
- Total trains: [X]
- Fastest: [Train name] in [Duration]
- Most frequent: [Details]

═══════════════════════════════════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════════

If tools fail or return errors:
- DON'T show technical error messages
- DO explain in simple terms: "I'm having trouble accessing the railway database right now. Please try again in a moment."
- DO offer alternative help or suggestions

If information is incomplete:
- Provide what you have
- Clearly state what's missing
- Suggest alternatives

═══════════════════════════════════════════════════════════════════════════════
COMMUNICATION STYLE
═══════════════════════════════════════════════════════════════════════════════

• Be conversational and friendly
• Use proper grammar and complete sentences
• Structure information with headers and bullet points
• Always offer to help with follow-up questions
• Include relevant disclaimers about real-time data

Remember: Your responses must ONLY contain natural language text that a human traveler can easily read and understand. No JSON, no function calls, no technical syntax - ever.
""",
    tools=[
        greeting, 
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "mcp-remote",
                        config.MCP_ENDPOINT,  # MCP endpoint from config
                    ],
                ),
                timeout=config.MCP_TIMEOUT  # Timeout from config (default: 6 minutes)
            ),
        )
    ],
)

# Create the AdkApp instance for deployment
agent_app = AdkApp(
    agent=root_agent,
    session_service_builder=session_service_builder
)

# Startup function for the agent engine
def startup():
    """Initialize the agent engine for deployment."""
    logger.info("Starting Indian Railway Assistant Agent Engine...")
    logger.info(f"Using MCP endpoint: {config.MCP_ENDPOINT}")
    logger.info(f"Model: {config.MODEL_NAME}")
    return agent_app

# Main entry point
if __name__ == "__main__":
    startup()
