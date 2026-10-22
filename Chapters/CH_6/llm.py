from langchain.chat_models import init_chat_model

def get_llm(model_name: str = "gpt-5-nano", temperature: float = 0):
    """
    Returns a ChatOpenAI instance with the specified model name and temperature.
    """
    from Chapters.CH_4.check_status import check_status
    model_name, provider = check_status()

    llm_openai = init_chat_model(model=model_name, model_provider=provider, temperature=temperature)
    return llm_openai

