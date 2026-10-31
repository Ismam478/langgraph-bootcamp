from langchain_core.messages import HumanMessage

import Chapters.CH_11.chatbot_with_template as bot
from Chapters.CH_11.prompts import build_messages


def test_template_renders_both_variables():
    msgs = build_messages([HumanMessage("Hi")], tone="formal", audience="experts")
    assert msgs[0].type == "system"
    assert "formal" in msgs[0].content
    assert "experts" in msgs[0].content


def test_history_follows_system_message_unchanged():
    msgs = build_messages([HumanMessage("Hi")])
    assert [m.type for m in msgs] == ["system", "human"]
    assert msgs[1].content == "Hi"


def test_different_tone_gives_different_system_prompt():
    friendly = build_messages([HumanMessage("Hi")], tone="friendly")[0].content
    formal = build_messages([HumanMessage("Hi")], tone="formal")[0].content
    assert friendly != formal


def test_chatbot_sends_templated_messages(fake_llm, monkeypatch):
    monkeypatch.setattr(bot, "get_llm", lambda: fake_llm)
    bot.chat_graph.invoke({"messages": [HumanMessage("Explain loops")]})
    sent = fake_llm.calls[0]
    assert sent[0].type == "system"
    assert sent[-1].content == "Explain loops"
