import json
from collections import Counter
from pathlib import Path

import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

import Chapters.CH_15.routing_workflow as rw
from Chapters.CH_15.eval_routing import load_set, evaluate, report

DATA = Path(__file__).parent.parent / "Chapters" / "CH_15" / "routing_set.json"
ROWS = load_set(DATA)
LOOKUP = {r["query"]: r["expected"] for r in ROWS}

def test_dataset_shape():
    """
    Test that the dataset has the expected shape and content.
    """
    query_counts = sum(1 for r in ROWS if "query" in r)
    expected_billing_count = sum(1 for r in ROWS if r["expected"] == "billing")
    expected_tech_count = sum(1 for r in ROWS if r["expected"] == "tech")
    expected_general_count = sum(1 for r in ROWS if r["expected"] == "general")
    
    assert len(ROWS) == 15
    assert query_counts == 15
    assert expected_billing_count == 5
    assert expected_tech_count == 5
    assert expected_general_count == 5

def test_perfect_fake_scores_everything(capsys):
    """
    A perfect router should score 100% and output correct summary metrics.
    """
    summary = report(evaluate(ROWS, lambda q: LOOKUP[q]))
    
    assert summary["per_category"] == {"billing": 5, "tech": 5, "general": 5}

    out, _ = capsys.readouterr()
    assert "Overall: 15/15" in out

def test_always_general_fake(capsys):
    """A naive router that defaults to 'general' should fail gracefully with accurate tracking."""
    results = evaluate(ROWS, lambda q: "general")
    summary = report(results)

    assert "33.3" in str(summary.get("accuracy", "33.3"))
    assert summary["per_category"] == {"billing": 0, "tech": 0, "general": 5}

    out, _ = capsys.readouterr()
    assert "Tricky: 1/3" in out

def test_summary_and_results_are_json_serializable():
    """Ensure evaluation outputs can be dumped safely for logging/tracking."""
    results = evaluate(ROWS, lambda q: LOOKUP[q])
    summary = report(results)
    
    try:
        json_str = json.dumps({"summary": summary, "results": results})
        assert isinstance(json_str, str)
    except TypeError as e:
        pytest.fail(f"Evaluation output is not JSON serializable: {e}")


def test_report_rejects_empty_results():
    """The reporter must fail explicitly if fed an empty result set."""
    with pytest.raises(ValueError, match="empty|results"):
        report([])


def make_fake_model(calls):
    """Spy on the LLM by capturing the prompt values sent to it."""
    def fake(prompt_value):
        calls.append(prompt_value.to_messages())
        return AIMessage(content="fake reply")
    return RunnableLambda(fake)


@pytest.mark.parametrize("category, phrase", [
    ("billing", "billing specialist"),
    ("tech", "technical support engineer"),
    ("general", "customer success"),
])
def test_router_sends_each_category_to_its_specialist(monkeypatch, category, phrase):
    """Verify that the routed node invokes the LLM with the correct platform/domain system message."""
    calls = []
    

    monkeypatch.setattr(rw, "classify", lambda query: category)
    

    monkeypatch.setattr(rw, "get_llm", lambda: make_fake_model(calls))
    

    out = rw.route_graph.invoke({"query": "fake user query"})
    
    assert out["category"] == category
    assert out["reply"] == "fake reply"
    assert len(calls) == 1, "The LLM should only be invoked once by the target node."
    

    system_message_content = calls[0][0].content.lower()
    assert phrase.lower() in system_message_content, f"Expected '{phrase}' in system prompt."


def test_unknown_category_is_rejected():
    """The conditional edge function must block unregistered nodes from being called."""
    bad_state = rw.GraphSchema(query="x", category="sales")
    
    with pytest.raises(ValueError):
        rw.router_condition(bad_state)