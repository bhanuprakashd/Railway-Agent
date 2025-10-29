import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "rajesh-more-cwx-internal")
    GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    MODEL_NAME = "gemini/gemini-2.5-flash"
    TEMPERATURE = 0.1
    MCP_ENDPOINT = "https://railway-mcp.amithv.xyz/mcp"
    MCP_TIMEOUT = 360
    LOG_LEVEL = "INFO"
    APP_NAME = "train_agent_app"
    BUCKET_NAME = "rajesh-more-cwx-internal-agent-engine"
