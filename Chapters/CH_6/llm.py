def get_llm(model_name: str = "gpt-5-nano", temperature: float = 0):
    """
    Returns a ChatOpenAI instance with the specified model name and temperature.
    """
    from langchain_openai import ChatOpenAI
    from Chapters.CH_4.check_status import check_status
    model_name, is_loaded = check_status()

    llm_openai = ChatOpenAI(model_name=model_name, temperature=temperature)
    return llm_openai

