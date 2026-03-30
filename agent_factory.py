from dataclasses import dataclass
from typing import Any, Sequence

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from common import RetryMCPInterceptor
from config import MODEL_NAME, TRAVEL_MCP_URL
from llm import get_openrouter_llm
from prompts import (
    PLAYLIST_AGENT_SYSTEM_PROMPT,
    TRAVEL_AGENT_SYSTEM_PROMPT,
    VENUE_AGENT_SYSTEM_PROMPT,
)
from tools import query_playlist_db, web_search


@dataclass(frozen=True)
class SpecialistAgents:
    travel_agent: Any
    venue_agent: Any
    playlist_agent: Any


async def fetch_travel_tools() -> Sequence[Any]:
    client = MultiServerMCPClient({
        "travel_server": {
            "transport": "streamable_http",
            "url": TRAVEL_MCP_URL,
        }
    }, tool_interceptors=[RetryMCPInterceptor()])
    return await client.get_tools()


def create_specialist_agents(travel_tools: Sequence[Any], model_name: str = MODEL_NAME) -> SpecialistAgents:
    travel_agent = create_agent(
        model=get_openrouter_llm(model_name=model_name),
        tools=list(travel_tools),
        system_prompt=TRAVEL_AGENT_SYSTEM_PROMPT,
    )

    venue_agent = create_agent(
        model=get_openrouter_llm(model_name=model_name),
        tools=[web_search],
        system_prompt=VENUE_AGENT_SYSTEM_PROMPT,
    )

    playlist_agent = create_agent(
        model=get_openrouter_llm(model_name=model_name),
        tools=[query_playlist_db],
        system_prompt=PLAYLIST_AGENT_SYSTEM_PROMPT,
    )

    return SpecialistAgents(
        travel_agent=travel_agent,
        venue_agent=venue_agent,
        playlist_agent=playlist_agent,
    )
