from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

def check_status():
    """
    Checks the status if the environment variables are loaded correctly and returns the model name and a boolean indicating if the variables are loaded.
    """

    import os

    required_vars = ["OPENAI_API_KEY", "AI_MODEL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    model = os.getenv("AI_MODEL")

    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("All required environment variables are loaded.")
        return model, True