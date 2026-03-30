from langchain.tools import tool
from tavily import TavilyClient
from typing import Dict, Any

from langchain_community.utilities import SQLDatabase

from config import TAVILY_API_KEY, DATABASE_URI

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
db = SQLDatabase.from_uri(DATABASE_URI)
@tool
def web_search(query: str, search_number: int, max_search_number: int) -> Dict[str, Any]:
    """Search the web for information. You must track your search count by providing
    search_number (starting at 1) and max_search_number on every call.
    Queries must use only plain text characters. Do not use accented or special characters     
    (e.g., use 'capacite' instead of 'capacité').
    """
    if search_number > max_search_number:
        return {"message": "Search limit reached. Please summarize your findings and provide your final answer."}
    try:
        return tavily_client.search(query)
    except Exception as e:
        return {"error": str(e)}


@tool
def query_playlist_db(query: str) -> str:
    """Query the database for playlist information"""
    try:
        return db.run(query)
    except Exception as e:
        return f"Error querying database: {e}"
