from typing import Any

from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from agent_factory import SpecialistAgents


def create_coordinator_tools(agents: SpecialistAgents) -> list[Any]:
    @tool
    async def search_flights(runtime: ToolRuntime) -> str:
        """Travel agent searches for flights to the desired destination wedding location."""
        origin = runtime.state["origin"]
        destination = runtime.state["destination"]
        response = await agents.travel_agent.ainvoke(
            {"messages": [HumanMessage(content=f"Find flights from {origin} to {destination}")]}
        )
        return response["messages"][-1].content

    @tool
    def search_venues(runtime: ToolRuntime) -> str:
        """Venue agent chooses the best venue for the given location and capacity."""
        destination = runtime.state["destination"]
        capacity = runtime.state["guest_count"]
        query = f"Find wedding venues in {destination} for {capacity} guests"
        response = agents.venue_agent.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content

    @tool
    def suggest_playlist(runtime: ToolRuntime) -> str:
        """Playlist agent curates the perfect playlist for the given genre."""
        genre = runtime.state["genre"]
        query = f"Find {genre} tracks for wedding playlist"
        response = agents.playlist_agent.invoke({"messages": [HumanMessage(content=query)]})
        return response["messages"][-1].content

    @tool
    def update_state(
        origin: str,
        destination: str,
        guest_count: str,
        genre: str,
        runtime: ToolRuntime,
    ) -> Command:
        """Update the state when all values are known so subsequent tools can use them."""
        return Command(update={
            "origin": origin,
            "destination": destination,
            "guest_count": guest_count,
            "genre": genre,
            "messages": [ToolMessage("Successfully updated state", tool_call_id=runtime.tool_call_id)]
        })

    return [update_state, search_flights, search_venues, suggest_playlist]
