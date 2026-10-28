from Chapters.CH_6.llm import get_llm


def get_completion_with_usage(prompt: str, system: str = "You are a helpful assistant.", temperature: float = 0):
    """
    Sends a system + user message to the LLM and returns (response, usage).
    """
    response = get_llm(temperature=temperature).invoke([("system", system), ("human", prompt)])
    usage = response.usage_metadata  

    print(f"Input tokens:  {usage['input_tokens']}")
    print(f"Output tokens: {usage['output_tokens']}")
    print(f"Total tokens:  {usage['total_tokens']}")
    print(f"Answer: {response.content}")
    return response, usage


def estimate_cost(usage: dict, price_in: float, price_out: float) -> float:
    """
    Estimated api cost in dollars.
    """
    cost_in = usage["input_tokens"] / 1_000_000 * price_in
    cost_out = usage["output_tokens"] / 1_000_000 * price_out
    return cost_in + cost_out


if __name__ == "__main__":
    # Look up the CURRENT prices for your model and put them here. (I'm using the OpenAI gpt-5-nano model prices as of 2025-08-07)
    PRICE_IN, PRICE_OUT = 0.05, 0.005  # dollars per 1M tokens

    _, usage = get_completion_with_usage("Explain what a token is in one sentence.")
    print(f"Estimated cost: ${estimate_cost(usage, PRICE_IN, PRICE_OUT):.6f}")
