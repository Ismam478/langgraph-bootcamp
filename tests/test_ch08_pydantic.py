import pytest
from pydantic import ValidationError

import Chapters.CH_8.pydantic_graph as m


def test_valid_input_runs(fake_llm, monkeypatch):
    monkeypatch.setattr(m, "get_llm", lambda: fake_llm)
    out = m.pydantic_graph.invoke({"input_text": "  Iron Man  "})
    assert out["result_text"] == "AI Message: fake reply"
    # The node receives the validated (stripped) value, so the LLM prompt has no
    # extra spaces. (The raw input is what stays stored in the final state.)
    assert fake_llm.calls[0] == "tell me 1 Line about this topic: Iron Man"


def test_too_short_after_stripping_is_rejected(fake_llm, monkeypatch):
    monkeypatch.setattr(m, "get_llm", lambda: fake_llm)
    with pytest.raises(ValidationError):
        m.pydantic_graph.invoke({"input_text": "  a "})
    assert fake_llm.calls == []  # failed before any node ran


def test_too_long_is_rejected():
    with pytest.raises(ValidationError):
        m.pydantic_graph.invoke({"input_text": "x" * 201})


def test_non_string_is_rejected():
    with pytest.raises(ValidationError):
        m.pydantic_graph.invoke({"input_text": 123})
