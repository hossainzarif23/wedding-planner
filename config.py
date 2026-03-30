from dotenv import load_dotenv
import os

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
RETRYABLE_MCP_CODES = {-32603}
DATABASE_URI = "sqlite:///resources/Chinook.db"
