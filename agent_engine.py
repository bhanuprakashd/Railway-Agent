import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AgentEngine
from config import config

# Initialize Vertex AI
vertexai.init(
    project=config.GOOGLE_CLOUD_PROJECT,
    location=config.GOOGLE_CLOUD_LOCATION,
    staging_bucket=f"gs://{config.BUCKET_NAME}"
)

# Create the agent engine for Indian Railway Assistant
remote_app = agent_engines.create(
    display_name="indian_railway_assistant",
    description="An intelligent Indian Railway assistant providing real-time train schedules, PNR status, seat availability, and station information through natural language conversation",
    agent_engine=agent_engines.ModuleAgent(
        module_name="root_agent",
        agent_name="agent_app",
        register_operations={
            "": ["get_session", "list_sessions", "create_session", "delete_session"],
            "async": [
                "async_get_session",
                "async_list_sessions",
                "async_create_session",
                "async_delete_session",
            ],
            "stream": ["stream_query", "streaming_agent_run_with_events"],
            "async_stream": ["async_stream_query"],
        },
    ),
    requirements=[
        "google-cloud-aiplatform[agent_engines,adk]>=1.101.0",
        "python-dotenv>=1.0.0",
        "mcp>=1.0.0",
    ],
    extra_packages=[
        "root_agent.py",
        "config.py",
        "installation_scripts/install_mcp.sh",
    ],
    env_vars={
        "GOOGLE_API_KEY": config.GOOGLE_API_KEY,
        "MCP_ENDPOINT": config.MCP_ENDPOINT,
        "BUCKET_NAME": config.BUCKET_NAME,
    },
    build_options={
        "installation": [
            "installation_scripts/install_mcp.sh",
        ],
    },
)