from langchain_openai import ChatOpenAI
from check_status import check_status

model, is_loaded = check_status()

def get_llm(model_name: str = model, temperature: float = 0):
    """
    Returns a ChatOpenAI instance with the specified model name and temperature.
    """
    llm_openai = ChatOpenAI(model_name=model_name, temperature=temperature)
    return llm_openai

