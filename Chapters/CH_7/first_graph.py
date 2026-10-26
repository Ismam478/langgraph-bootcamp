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
    error_text: str = "" # Default value for error_text


def validate_input(state: State) -> State:
    """
    Validates the input text in the state.
    """

    msg = state["input_text"]

    if type(msg) != str:
        return {"error_text": "Message is not available"}
    
    if not msg or msg.strip() == "":
        return {"error_text": "Message is empty"}
        
    if msg and type(msg) == str:
        msg = msg.strip()
        if len(msg) > 150:
            return {'error_text': "Message is more than 150 words"}
        
        return {"input_text": msg, "error_text": ""}
    

def route_after_validate(state: State) -> Literal["error", "process"]:
    return "error" if state["error_text"] else "process"

def process_text(state: State)-> State:
    """
    Processes The Input Text.
    """

    curr_msg = state["input_text"]

    if state["error_text"] == "":
        result = llm_openai.invoke(curr_msg)

    return {"result_text": f"AI Message: {result.content}"}

def error_text(state: State) -> State:
    """
    Handles the error text in the state.
    """

    if state["error_text"]:
        return {"result_text": f"Error: {state['error_text']}"}


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
    # result = first_graph.invoke({"input_text": "Hello, How are you?"})
    # display(Image(first_graph.get_graph().draw_mermaid_png()))

    # print(result)
    for test in ["", "     ", "hello", "x" * 151, 12345]:
        try:
            print(repr(test)[:20], "->", first_graph.invoke({"input_text": test}))
        except Exception as e:
            print(repr(test)[:20], "-> CRASH:", type(e).__name__, e)