from Chapters.CH_6.llm import get_llm
from pydantic import BaseModel, Field, field_validator
from langgraph.graph import StateGraph, START, END

llm_openai = get_llm()

class State(BaseModel):
    input_text: str = Field(..., description="The input text to be processed", min_length=3, max_length=200)
    result_text: str = Field(default="", description="The result text after processing")

    @field_validator("input_text")
    @classmethod
    def validate_input(cls, text: str) -> str:
        return text.strip() if isinstance(text, str) else text

def process_text(state: State) -> State:
    """
    Processes the input text.
    """

    curr_msg = state.input_text

    result = llm_openai.invoke(f"tell me 1 Line about this topic: {curr_msg}")
    state.result_text = f"AI Message: {result.content}"

    return state


graph = StateGraph(State)

graph.add_node("process_text", process_text)

graph.add_edge(START, "process_text")
graph.add_edge("process_text", END)


pydantic_graph = graph.compile()


if __name__ == "__main__":
    result = pydantic_graph.invoke({"input_text": "Iron Man"})

    print(result)