from Chapters.CH_6.llm import get_llm
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage

SYSTEM_PROMPT = "You are a helpful assistant. Keep answers short."

def chatbot(state: MessagesState) -> MessagesState:
    """
    A simple chatbot that uses a language model to generate responses based on user input.
    """
    llm = get_llm()

    result = llm.invoke([SystemMessage(content=SYSTEM_PROMPT)] + state["messages"])
    return {'messages' : [result]}

builder = StateGraph(MessagesState)
builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)
chat_graph = builder.compile()

history = []
while True:
    user_input = input("User: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    history.append(HumanMessage(content=user_input))
    history = chat_graph.invoke({"messages": history})['messages']
    print("AI:", history[-1].content)

