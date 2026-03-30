from langchain_openrouter import ChatOpenRouter

from config import OPENROUTER_API_KEY

def get_openrouter_llm(model_name: str, max_completion_tokens: int = 4096):
    return ChatOpenRouter(
        model=model_name,
        api_key=OPENROUTER_API_KEY,
        temperature=0.0,
        seed=42,
        max_completion_tokens=max_completion_tokens
    )
