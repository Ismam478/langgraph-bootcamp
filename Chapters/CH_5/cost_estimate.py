from langchain_openai import ChatOpenAI

def get_completion_with_usage(prompt: str, model_name: str = "gpt-5-nano", temperature: float = 0):
    """
    Takes in User prompt and returns the completion along with Token Usage information.
    """

    from Chapters.CH_4.check_status import check_status
    model_name, is_loaded = check_status()

    llm_openai = ChatOpenAI(model_name=model_name, temperature=temperature)
    response = llm_openai.invoke(prompt)
    token_usage = response.response_metadata['token_usage']

    print(f"Completion Token Usage: {token_usage['completion_tokens']}")
    print(f"Prompt Token Usage: {token_usage['prompt_tokens']}")
    print(f"Total Token Usage: {token_usage['total_tokens']}")
    print(f"Answer: {response.content}")

    return response, token_usage


def cost_estimate(token_usage: dict, model_name: str = "gpt-5-nano"):
    """
    Takes in Token Usage information and estimates the cost based on the model's pricing.
    """

    pricing = {
        "gpt-5-nano": 0.0004,
        "gpt-5-mini": 0.0008,
        "gpt-5-medium": 0.0016,
        "gpt-5-large": 0.0032,
        "gpt-5-xl": 0.0064
    }

    if model_name not in pricing:
        raise ValueError(f"Pricing information for model '{model_name}' is not available.")

    cost_per_1k_tokens = pricing[model_name]
    total_tokens = token_usage['total_tokens']
    estimated_cost = (total_tokens / 1000) * cost_per_1k_tokens

    print(f"Estimated Cost for {total_tokens} tokens using {model_name}: ${estimated_cost:.6f}")
    return estimated_cost

