from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
RETRYABLE_MCP_CODES = {-32603}
DATABASE_URI = "sqlite:///resources/Chinook.db"
MODEL_NAME = "qwen/qwen3.5-35b-a3b"
TRAVEL_MCP_URL = "https://mcp.kiwi.com"
COORDINATOR_RECURSION_LIMIT = 40
APP_TAGS = ["WP"]
