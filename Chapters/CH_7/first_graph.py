from Chapters.CH_6.llm import get_llm
from typing import TypedDict, Literal
from pydantic import Field
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display

llm_openai = get_llm()

# Defining a TypedDict State
class State(TypedDict):
    input_text: str 
    result_text: str 
    error_text: str 


def validate_input(state: State) -> State:
    """
    Validates the input text in the state.
    """

    msg = state["input_text"]
    msg = msg.strip()

    if type(msg) != str:
        state["error_text"] = "Message is not available"
    elif len(msg) > 100:
        state["error_text"] = "Message is more than 100 words"
    else:
        state["error_text"] = ""

    return state

def route_after_validate(state: State) -> Literal["error", "process"]:
    return "error" if state["error_text"] else "process"

def process_text(state: State)-> State:
    """
    Processes The Input Text.
    """

    curr_msg = state["input_text"]

    if state["error_text"] == "":
        result = llm_openai.invoke(curr_msg)
        state["result_text"] = f"AI Message: {result.content}"

    return state

def error_text(state: State) -> State:
    """
    Handles the error text in the state.
    """

    if state["error_text"] != "":
        state["result_text"] = f"Error: {state['error_text']}"

    
    return state


graph = StateGraph(State)

graph.add_node("validate_text", validate_input)
graph.add_node("error_text", error_text)
graph.add_node("process_text", process_text)

graph.add_edge(START, "validate_text")
graph.add_conditional_edges("validate_text", route_after_validate, {"error": "error_text", "process": "process_text"})
graph.add_edge("error_text", END)
graph.add_edge("process_text", END)


first_graph = graph.compile()

if __name__ == "__main__":
    result = first_graph.invoke({"input_text": "Hello, How are you?"})
    display(Image(first_graph.get_graph().draw_mermaid_png()))

    print(result)