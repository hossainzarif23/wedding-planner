from typing import Any

from langchain.agents import create_agent
from langchain.messages import HumanMessage

from agent_factory import create_specialist_agents, fetch_travel_tools
from config import APP_TAGS, COORDINATOR_RECURSION_LIMIT, MODEL_NAME
from coordinator_tools import create_coordinator_tools
from llm import get_openrouter_llm
from prompts import COORDINATOR_AGENT_SYSTEM_PROMPT
from states import WeddingState


async def run_wedding_planner(user_request: str) -> dict[str, Any]:
    travel_tools = await fetch_travel_tools()
    specialist_agents = create_specialist_agents(travel_tools=travel_tools, model_name=MODEL_NAME)

    coordinator_agent = create_agent(
        model=get_openrouter_llm(model_name=MODEL_NAME),
        tools=create_coordinator_tools(specialist_agents),
        system_prompt=COORDINATOR_AGENT_SYSTEM_PROMPT,
        state_schema=WeddingState,
    )

    return await coordinator_agent.ainvoke(
        {"messages": [HumanMessage(content=user_request)]},
        config={"tags": APP_TAGS, "recursion_limit": COORDINATOR_RECURSION_LIMIT},
    )
