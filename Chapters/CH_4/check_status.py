from dotenv import load_dotenv, find_dotenv
import sys
from importlib.metadata import version

load_dotenv(find_dotenv())

required_vars = ["OPENAI_API_KEY", "AI_MODEL", "PROVIDER"]

def check_status():
    """
    Checks the status if the environment variables are loaded correctly.
    """

    import os

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        sys.exit(f"Missing env vars: {', '.join(missing_vars)}. Please set them in your .env file.")

    model = os.getenv("AI_MODEL")
    provider = os.getenv("PROVIDER")
    print(f"LangGraph Version: {version('langgraph')}")
    print(f"Model: {model}, Provider: {provider}")
    
    return model, provider


if __name__ == "__main__":
    check_status()