from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph import add_messages
from langchain_core.messages import AIMessage, HumanMessage, RemoveMessage

def own_reducer(old: list, new: list) -> list:
    """
    Combines existing state (old) and incoming updates (new), 
    preserving order while keeping only unique items.
    """
    merged = list(old)
    for item in new:
        if item not in merged:
            merged.append(item)
    return merged

class StateA(TypedDict):
    messages: List

class StateB(TypedDict):
    messages: Annotated[List, add_messages]

class StateC(TypedDict):
    messages: Annotated[List, own_reducer]

def node_one(state):
    return {"messages": [AIMessage(content="one")]}

def node_two(state):
    return {"messages": [AIMessage(content="two")]}

def delete_first(state):
    return {"messages": [RemoveMessage(id=state["messages"][0].id)]}

def build(state):
    graph = StateGraph(state)

    graph.add_node("one", node_one)
    graph.add_node("two", node_two)
    graph.add_node("delete_first", delete_first)

    graph.add_edge(START, "one")
    graph.add_edge("one", "two")
    graph.add_edge("two", "delete_first")
    graph.add_edge("delete_first", END)


    return graph.compile()


if __name__ == "__main__":
    start = {"messages": [HumanMessage(content="Iron Man")]}
    print([m.content for m in build(StateA).invoke(start)["messages"]])
    print([m.content for m in build(StateB).invoke(start)["messages"]])
    print([m.content for m in build(StateC).invoke(start)["messages"]])
    print(f"\n\n\nMessagesState: {[m.content for m in build(MessagesState).invoke(start)["messages"]]}")