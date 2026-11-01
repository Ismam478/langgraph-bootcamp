import pytest
from langchain_core.messages import AIMessage


class FakeLLM:
    """Stands in for a real chat model: no API call, no cost, records what it was sent."""

    def __init__(self, reply="fake reply"):
        self.reply = reply
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(content=self.reply)


@pytest.fixture
def fake_llm():
    return FakeLLM()
