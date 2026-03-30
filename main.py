import asyncio
from pprint import pprint

from workflow import run_wedding_planner

async def main():
    response = await run_wedding_planner(user_request="I'm from London and I'd like a wedding in Paris for 100 guests, jazz-genre")
    pprint(response)
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
