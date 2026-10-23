from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, trim_messages
from Chapters.CH_6.llm import get_llm

SYSTEM_PROMPT = "You are a helpful assistant. Keep answers short."

def trimmed_chatbot(state: MessagesState):
    trimmed = trim_messages(
        state["messages"],
        max_tokens=6,
        token_counter=len,
        strategy="last",
        start_on="human",
    )
    reply = get_llm().invoke([SystemMessage(SYSTEM_PROMPT)] + trimmed)
    return {"messages": [reply]}

builder = StateGraph(MessagesState)
builder.add_node("chatbot", trimmed_chatbot)
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