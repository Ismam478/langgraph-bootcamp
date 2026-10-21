from Chapters.CH_6.llm import get_llm
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

llm_openai = get_llm()

class State(BaseModel):
    input_text: str = Field(..., description="The input text to be processed", min_length=3, max_length=200)
    result_text: str = Field(default="", description="The result text after processing")
    error_text: str = Field(default="", description="The error text if any validation fails")


def validate_input(state: State) -> State:
    """
    Validates the input text in the state.
    """

    msg = state.input_text.strip()

    if not isinstance(msg, str):
        state.error_text = "Message is not available"
    # elif len(msg) < 3:
    #     state.error_text = "Message is less than 3 words"
    # elif len(msg) > 200:
    #     state.error_text = "Message is more than 200 words"

    return state

def process_text(state: State) -> State:
    """
    Processes the input text.
    """

    curr_msg = state.input_text

    if state.error_text == "":
        result = llm_openai.invoke(curr_msg)
        state.result_text = f"AI Message: {result.content}"

    return state


def error_text(state: State) -> State:
    """
    Handles the error text in the state.
    """

    if state.error_text != "":
        state.result_text = f"Error: {state.error_text}"

    return state

graph = StateGraph(State)

graph.add_node("validate_text", validate_input)
graph.add_node("error_text", error_text)
graph.add_node("process_text", process_text)

graph.add_edge(START, "validate_text")
graph.add_edge("validate_text", "error_text")
graph.add_edge("error_text", "process_text")
graph.add_edge("process_text", END)


pydantic_graph = graph.compile()

result = pydantic_graph.invoke({"input_text": "Hello, How are you?"})


print(result)