from dotenv import load_dotenv, find_dotenv
from importlib.metadata import version

load_dotenv(find_dotenv())

def check_status():
    """
    Checks the status if the environment variables are loaded correctly.
    """

    import os

    required_vars = ["OPENAI_API_KEY", "AI_MODEL", "PROVIDER"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    model = os.getenv("AI_MODEL")
    provider = os.getenv("PROVIDER")

    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")

    print(f"LangGraph Version: {version('langgraph')}")
    print(f"Model: {model}, Provider: {provider}")
    return model, provider
        