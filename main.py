import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import ToolRuntime, tool
from langchain.messages import HumanMessage, ToolMessage
from langgraph.types import Command
from langchain.agents import create_agent
from pprint import pprint

from common import RetryMCPInterceptor
from llm import get_openrouter_llm
from prompts import TRAVEL_AGENT_SYSTEM_PROMPT, VENUE_AGENT_SYSTEM_PROMPT, PLAYLIST_AGENT_SYSTEM_PROMPT, COORDINATOR_AGENT_SYSTEM_PROMPT
from states import WeddingState
from tools import web_search, query_playlist_db

travel_agent_tools = None

async def get_tools():
    client = MultiServerMCPClient({
        "travel_server": {
            "transport": "streamable_http",
            "url": "https://mcp.kiwi.com"
        }
    }, tool_interceptors=[RetryMCPInterceptor()])
    
    tools = await client.get_tools()
    
    return tools

async def main():
    travel_agent_tools = await get_tools()

    travel_agent_llm = get_openrouter_llm(model_name="qwen/qwen3.5-35b-a3b")
    venue_agent_llm = get_openrouter_llm(model_name="qwen/qwen3.5-35b-a3b")
    playlist_agent_llm = get_openrouter_llm(model_name="qwen/qwen3.5-35b-a3b")
    coordinator_llm = get_openrouter_llm(model_name="qwen/qwen3.5-35b-a3b")

    travel_agent = create_agent(
        model=travel_agent_llm,
        tools=travel_agent_tools,
        system_prompt=TRAVEL_AGENT_SYSTEM_PROMPT
    )

    venue_agent = create_agent(
        model=venue_agent_llm,
        tools=[web_search],
        system_prompt=VENUE_AGENT_SYSTEM_PROMPT
    )

    playlist_agent = create_agent(
        model=playlist_agent_llm,
        tools=[query_playlist_db],
        system_prompt=PLAYLIST_AGENT_SYSTEM_PROMPT
    )

    @tool
    async def search_flights(runtime: ToolRuntime) -> str:
        """Travel agent searches for flights to the desired destination wedding location."""
        origin = runtime.state["origin"]
        destination = runtime.state["destination"]
        response = await travel_agent.ainvoke({"messages": [HumanMessage(content=f"Find flights from {origin} to {destination}")]})
        return response['messages'][-1].content

    @tool
    def search_venues(runtime: ToolRuntime) -> str:
        """Venue agent chooses the best venue for the given location and capacity."""
        destination = runtime.state["destination"]
        capacity = runtime.state["guest_count"]
        query = f"Find wedding venues in {destination} for {capacity} guests"
        response = venue_agent.invoke({"messages": [HumanMessage(content=query)]})
        return response['messages'][-1].content

    @tool
    def suggest_playlist(runtime: ToolRuntime) -> str:
        """Playlist agent curates the perfect playlist for the given genre."""
        genre = runtime.state["genre"]
        query = f"Find {genre} tracks for wedding playlist"
        response = playlist_agent.invoke({"messages": [HumanMessage(content=query)]})
        return response['messages'][-1].content

    @tool
    def update_state(origin: str, destination: str, guest_count: str, genre: str, runtime: ToolRuntime) -> Command:
        """Update the state when you know all of the values: origin, destination, guest_count, genre. 
        This tool must be called alone, without any other tool calls. It must complete and return to make,
        the information available to other tools."""
        return Command(update={
            "origin": origin, 
            "destination": destination, 
            "guest_count": guest_count, 
            "genre": genre, 
            "messages": [ToolMessage("Successfully updated state", tool_call_id=runtime.tool_call_id)]
        })

    coordinator_agent = create_agent(
        model=coordinator_llm,
        tools=[update_state, search_flights, search_venues, suggest_playlist],
        system_prompt=COORDINATOR_AGENT_SYSTEM_PROMPT,
        state_schema=WeddingState
    )

    response = await coordinator_agent.ainvoke(
        {"messages": [HumanMessage(content="I'm from London and I'd like a wedding in Paris for 100 guests, jazz-genre")]},
        config={"tags": ["WP"], "recursion_limit": 40}
    )

    pprint(response)
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
