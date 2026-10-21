from Chapters.CH_6.llm import get_llm
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

llm_openai = get_llm()

# Defining a TypedDict State
class State(TypedDict):
    input_text: str
    result_text: str
    error_text: str


def validate_input(state: State) -> bool:
    """
    Validates the input text in the state.
    Returns True if valid, False otherwise.
    """

    msg = state['input_text']

    if not msg or len(msg)>100:
        state["error_text"] = "Either Message is not available or the Message is more than 100 words"

        return state


def process_text(state: State)-> State:
    """
    Processes The Input Text.
    """

    curr_msg = state["input_text"]

    if not state["error_text"]:
        result = llm_openai.invoke(curr_msg)
        state["result_text"] = f"AI Message: {result.content}"

    return state


graph = StateGraph(State)

graph.add_node("validate_text", validate_input)
graph.add_node("process_text", process_text)

graph.add_edge(START, "validate_text")
graph.add_edge("validate_text", "process_text")
graph.add_edge("process_text", END)


first_graph = graph.compile()
display(Image(first_graph.get_graph().draw_mermaid_png()))


result = first_graph.invoke({"input_text": "Hello, How are you? I am testing the LangGraph library. It is a great library for building state machines and graphs. I am excited to see how it works!"})

print(result)



