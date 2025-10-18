import asyncio
import os
import logging
from google.adk import Agent, Runner
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# Import configuration
try:
    from config import config
except ImportError:
    # Fallback to default values if config module not available
    class config:
        OLLAMA_API_BASE = "http://localhost:11434"
        MODEL_NAME = "ollama/glm-4.6:cloud"
        TEMPERATURE = 0.1
        MCP_ENDPOINT = "https://railway-mcp.amithv.xyz/mcp"
        MCP_TIMEOUT = 360
        LOG_LEVEL = "INFO"
        APP_NAME = "train_agent_app"

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set Ollama API base from config
os.environ["OLLAMA_API_BASE"] = config.OLLAMA_API_BASE

# Initialize LLM with configuration
llm = LiteLlm(
    model=config.MODEL_NAME,
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

# Initialize MCP toolset
# Using Indian Railway MCP Server: https://github.com/amith-vp/indian-railway-mcp
# This provides real-time access to Indian Railway data through MCP protocol
mcp_toolset = MCPToolset(
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

# ════════════════════════════════════════════════════════
# ROOT AGENT CONFIGURATION
# ════════════════════════════════════════════════════════
"""
Train_Agent - Indian Railway Information Assistant

DESCRIPTION:
An intelligent conversational agent that provides comprehensive Indian Railway 
information through natural language interaction. Powered by Google ADK and 
connected to real-time railway data via Model Context Protocol (MCP).

CAPABILITIES:
• Train Search & Scheduling - Find trains between any two stations
• Live Train Status - Real-time tracking and delay information
• PNR Status Checking - Verify booking status and seat confirmation
• Seat Availability - Check available seats across all classes
• Station Information - Get station codes, facilities, and details
• Route Planning - Optimal journey suggestions with connections

TECHNICAL ARCHITECTURE:
• LLM: Ollama GLM-4.6 (cloud edition) via LiteLLM
• Tools: MCP Toolset + Custom greeting function
• Data Source: Indian Railway MCP Server (github.com/amith-vp/indian-railway-mcp)
• MCP Endpoint: railway-mcp.amithv.xyz
• Session Management: In-memory persistent sessions
• Response Format: Human-readable natural language only

KEY FEATURES:
• Context-aware conversations with memory across interactions
• Structured output formatting (tables, bullet points, markdown)
• Error handling with user-friendly fallback messages
• Real-time data validation and sanitization
• Multi-turn dialogue support for complex queries

USE CASES:
1. Travel Planning - "Show trains from Delhi to Mumbai tomorrow"
2. Booking Assistance - "Check seat availability in 3AC for train 12345"
3. Journey Tracking - "Where is train 12760 right now?"
4. Status Updates - "Check PNR 1234567890"
5. Station Queries - "What's the station code for Hyderabad?"

OUTPUT REQUIREMENTS:
• Plain English responses only (no JSON/code)
• Structured formatting with tables and lists
• Contextual recommendations and alternatives
• Clear error messages without technical jargon
• Conversational tone with helpful suggestions

AGENT METADATA:
• Version: 1.0.0
• Language: English (Indian context)
• Domain: Indian Railways Transportation
• Response Time: ~2-5 seconds (depending on query complexity)
• Accuracy: Real-time data from official railway systems
"""

# Create root agent
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
        mcp_toolset
    ],
)

# ════════════════════════════════════════════════════════
# GLOBAL SESSION MANAGEMENT
# ════════════════════════════════════════════════════════
_session_service = None
_runner = None
_session = None
_user_id = "user123"  # TODO: Make this dynamic per user when authentication is added
_app_name = config.APP_NAME

async def initialize_session():
    """Initialize session service, runner, and session once"""
    global _session_service, _runner, _session
    
    if _session_service is None:
        _session_service = InMemorySessionService()
        logger.info("Created new session service")
    
    if _runner is None:
        _runner = Runner(
            agent=root_agent,
            app_name=_app_name,
            session_service=_session_service
        )
        logger.info("Created new runner")
    
    if _session is None:
        _session = await _session_service.create_session(
            user_id=_user_id,
            app_name=_app_name
        )
        logger.info(f"Created new session: {_session.id}")
    
    return _session_service, _runner, _session

async def workflow(query: str):
    """Main workflow that maintains session and MCP connection across calls"""
    global _session_service, _runner, _session
    
    # WORKAROUND: Reset session for each query to avoid MCP state corruption
    # This ensures tools execute properly and generate natural language
    # Trade-off: Loses conversation context but ensures correct responses
    await reset_session()
    
    # Initialize session if not already done
    session_service, runner, session = await initialize_session()
    
    new_message = types.Content(role="user", parts=[types.Part(text=query)])
    final_response = ""
    all_responses = []
    logger.info(f"User Query: {query}")
    logger.debug(f"Using session: {session.id}")
    logger.debug(f"MCP Toolset active: {mcp_toolset is not None}")
    
    async for event in runner.run_async(
        user_id=_user_id, 
        session_id=session.id, 
        new_message=new_message
    ):
        event_type = type(event).__name__
        logger.info(f"📩 Event type: {event_type}, is_final: {event.is_final_response() if hasattr(event, 'is_final_response') else 'N/A'}")
        
        # Log ALL content to debug
        if hasattr(event, 'content'):
            if hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        logger.info(f"📝 Content preview: {part.text[:150]}...")
        
        # Collect ALL responses, not just the first one
        if event.is_final_response():
            # Extract text from the response
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text = part.text
                        all_responses.append(response_text)
                        logger.info(f"✅ Collected response #{len(all_responses)}: {response_text[:100]}...")
    
    # Process all collected responses
    # Skip tool call responses and use the last natural language response
    for response in reversed(all_responses):  # Start from the most recent
        # Check if this is a natural language response (not a tool call)
        if "Tool Calls:" not in response and '"type": "function"' not in response and len(response) > 50:
            final_response = response
            logger.info(f"Using natural language response: {final_response[:100]}...")
            break
    
    # If we only got tool calls, warn about it
    if not final_response and all_responses:
        logger.warning(f"Only received tool call responses, no natural language. Responses count: {len(all_responses)}")
        logger.debug(f"Last response was: {all_responses[-1][:200]}...")
        final_response = "I apologize, but I'm having trouble formatting the response. Please try asking in a different way."
    
    # If no response was captured at all, return a fallback message
    if not final_response:
        final_response = "I apologize, but I couldn't process that request. Please try again."
        logger.warning("No response captured from agent")
    
    return final_response

async def reset_session():
    """Reset session (useful for starting new conversation)"""
    global _session_service, _runner, _session
    _session_service = None
    _runner = None
    _session = None
    logger.info("Session reset")

if __name__ == "__main__":
    asyncio.run(workflow(query="get info of 12760 train"))
