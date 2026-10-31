"""
Run: uv run python -m Chapters.CH_11.tone_demo
"""
from langchain_core.messages import HumanMessage

from Chapters.CH_11.chatbot_with_template import chat_graph
from Chapters.CH_11.prompts import TONE, AUDIENCE

if __name__ == "__main__":
    out = chat_graph.invoke({"messages": [HumanMessage("Explain what a variable is.")]})
    print(f"TONE={TONE}, AUDIENCE={AUDIENCE}")
    print(out["messages"][-1].content)
