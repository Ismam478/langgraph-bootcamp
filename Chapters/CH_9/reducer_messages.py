from Chapters.CH_6.llm import get_llm
from typing import TypedDict, Annotated, List
from operator import add
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage, HumanMessage

llm_openai = get_llm()

class graph_schema(TypedDict):
    input_text: str
    messages_manual: List
    messages_auto: Annotated[List, add]

def researcher(state: graph_schema) -> graph_schema:
    """
    researches about the input topic using the LLM.
    """
    curr_msg = []
    curr_msg.append(state["input_text"])
    messages_auto = state["messages_auto"]

    if curr_msg:
        result = llm_openai.invoke(f"Tell me in 2 lines about: {curr_msg}").content
        state["messages_manual"] = curr_msg + [AIMessage(content=result)]
        state["messages_auto"] = [AIMessage(content=result)]
        state["input_text"] = result
        
    return state

def summarizer(state: graph_schema) -> graph_schema:
    """
    Summarizes the messages using the LLM.
    """
    curr_msg = []
    curr_msg.append(state["input_text"])
    messages_auto = state["messages_auto"]

    if curr_msg:
        result = llm_openai.invoke(f"Summarize it 1 line: {curr_msg}").content
        state["messages_manual"] = curr_msg + [AIMessage(content=result)]
        state["messages_auto"] = [AIMessage(content=result)]
        state["input_text"] = result

    return state

graph = StateGraph(graph_schema)

graph.add_node("researcher", researcher)
graph.add_node("summarizer", summarizer)


graph.add_edge(START, "researcher")
graph.add_edge("researcher", "summarizer")
graph.add_edge("summarizer", END)

auto_messages_graph = graph.compile()

if __name__ == "__main__":
    result = auto_messages_graph.invoke({"input_text":[HumanMessage(content="Iron Man")]})

    final_auto_results = result['messages_auto']
    final_manual_results = result['messages_manual']

    print(final_auto_results)
    print("\n\n\n\n")
    print(final_manual_results)
