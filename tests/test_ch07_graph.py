from Chapters.CH_7.first_graph import validate_input
import Chapters.CH_7.first_graph as first_graph_module

def test_empty_input_is_rejected():
    result = validate_input({"input_text": ''})
    assert result == {"error_text": "Message is empty"}

def test_whitespace_only_is_rejected():
    result = validate_input({"input_text": '   '})
    assert result == {"error_text": "Message is empty"}

def test_text_is_stripped():
    result = validate_input({"input_text": "   hello   "})
    assert result == {"input_text": "hello", "error_text": ""}

def test_exactly_at_limit_is_accepted():
    result = validate_input({"input_text": "x" * 150})
    assert result == {"input_text": "x" * 150, "error_text": ""}

def test_one_over_limit_is_rejected():
    result = validate_input({"input_text": "x" * 151})
    assert result == {"error_text": "Message is more than 150 characters"}

def test_non_text_is_rejected():
    result = validate_input({"input_text": 12345})
    assert result == {"error_text": "Message is not available"}

class FakeLLM():
    def __init__(self):
        calls = []
        self.calls = calls

    def invoke(self, msg):
        from types import SimpleNamespace
        self.calls.append(msg)
        return SimpleNamespace(content=f"Hello, I am a fake LLM. You said: {msg}")

def test_graph_string(monkeypatch):
    fake_llm = FakeLLM()
    monkeypatch.setattr(first_graph_module, "llm_openai", fake_llm)
    result = first_graph_module.first_graph.invoke({"input_text": "hello"})
    assert len(first_graph_module.llm_openai.calls) == 1
    assert result == {'input_text': 'hello', "result_text": "AI Message: Hello, I am a fake LLM. You said: hello", 'error_text': ''}

def test_graph_blank(monkeypatch):
    fake_llm = FakeLLM()
    monkeypatch.setattr(first_graph_module, "llm_openai", fake_llm)
    result = first_graph_module.first_graph.invoke({"input_text": ""})
    assert len(first_graph_module.llm_openai.calls) == 0
    assert result == {'input_text': '', "result_text": "Error: Message is empty", 'error_text': "Message is empty"}

def test_graph_over_limit(monkeypatch):
    fake_llm = FakeLLM()
    monkeypatch.setattr(first_graph_module, "llm_openai", fake_llm)
    result = first_graph_module.first_graph.invoke({"input_text": "x"*151})
    assert len(first_graph_module.llm_openai.calls) == 0
    assert result == {'input_text': 'x'*151, "result_text": "Error: Message is more than 150 characters", 'error_text': "Message is more than 150 characters"}