import time
import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.types import Send

import Chapters.CH_16.orchestrator_workflow as ow
from Chapters.CH_16.orchestrator_workflow import clean_tasks, assign_workers, GraphSchema

# ---------- 1. clean_tasks (pure function, no fakes) ----------
def test_clean_tasks_strips_whitespace_and_blanks():
    raw_tasks = ["  task one  ", "", "      ", "task two"]
    cleaned = clean_tasks(raw_tasks, query="default query")
    assert cleaned == ["task one", "task two"]

def test_clean_tasks_removes_duplicates_keeps_order():
    raw_tasks = ["alpha", "beta", "alpha", "gamma", "beta"]
    cleaned = clean_tasks(raw_tasks, query="default query")
    assert cleaned == ["alpha", "beta", "gamma"]

def test_clean_tasks_caps_at_max_tasks():
    raw_tasks = [f"task {i}" for i in range(15)]
    cleaned = clean_tasks(raw_tasks, query="default query")
    assert len(cleaned) == ow.MAX_TASKS
    assert cleaned == [f"task {i}" for i in range(ow.MAX_TASKS)]

def test_clean_tasks_empty_falls_back_to_query():
    assert clean_tasks([], query="fallback query") == ["fallback query"]
    assert clean_tasks(["", "    "], query="fallback query") == ["fallback query"]

# ---------- 2. assign_workers (no LLM) ----------
def test_assign_workers_one_send_per_task():
    state = GraphSchema(query="test query", tasks=["task_a", "task_b", "task_c"])
    sends = assign_workers(state)
    
    assert len(sends) == 3
    for i, send in enumerate(sends):
        assert isinstance(send, Send)
        assert send.node == "worker_node"
        assert send.arg == {"task": f"task_{chr(97 + i)}", "index": i, "query": "test query"}

# ---------- 3. a fake model ----------
class FakeLLM(RunnableLambda):
    def __init__(self, plan, seen=None):
        self.seen = seen if seen is not None else []   # every prompt the fake receives
 
        def _reply(prompt_value):
            text = str(prompt_value)
            self.seen.append(text)
            if "This is the Task:" in text:             # worker prompt
                task = text.split("This is the Task: ")[1].split(" and query")[0]
                return AIMessage(content=f"Result of {task}")
            return AIMessage(content="Summary")         # collector prompt
 
        super().__init__(_reply)
        object.__setattr__(self, "_plan", plan)         # plan is a list of tasks, or an Exception
 
    def with_structured_output(self, schema):
        plan = self._plan
        def planner(_):
            if isinstance(plan, Exception):
                raise plan
            return schema(tasks=plan)
        return RunnableLambda(planner)

# ---------- 4. whole graph with the fake ----------
def test_planner_error_falls_back_to_single_task(monkeypatch):
    monkeypatch.setattr(ow, "get_llm", lambda *a, **k: FakeLLM(Exception("planner down")))
    out = ow.orchestrator_workflow.invoke({"query": "emergency query"})
    assert out["tasks"] == ["emergency query"]
    assert len(out["results"]) == 1
 
def test_planner_overflow_is_capped(monkeypatch):
    plan = [f"section {i}" for i in range(9)]
    monkeypatch.setattr(ow, "get_llm", lambda *a, **k: FakeLLM(plan))
    out = ow.orchestrator_workflow.invoke({"query": "overflow query"})
    assert len(out["tasks"]) == ow.MAX_TASKS
    assert len(out["results"]) == ow.MAX_TASKS          # the cap reached the workers too
 
def test_llm_calls_total_is_n_plus_two(monkeypatch):
    seen = []
    monkeypatch.setattr(ow, "get_llm", lambda *a, **k: FakeLLM(["a", "b", "c"], seen=seen))
    out = ow.orchestrator_workflow.invoke({"query": "counting query"})
    assert out["llm_calls"] == 3 + 2                    # planner + 3 workers + collector
    assert len(seen) == 3 + 1                           # independent check: fake saw 3 workers + collector
 
 
# ---------- 5. ordering ----------
# Through the whole graph this cannot be tested: LangGraph merges parallel updates
# in Send order, not finish order. So test collector_node directly with shuffled input.
def test_collector_sorts_shuffled_results(monkeypatch):
    seen = []
    monkeypatch.setattr(ow, "get_llm", lambda *a, **k: FakeLLM([], seen=seen))
    state = GraphSchema(
        query="q",
        results=[{"index": 1, "result": "SECOND"}, {"index": 0, "result": "FIRST"}],
    )
    ow.collector_node(state)
    prompt = seen[-1]
    assert prompt.index("FIRST") < prompt.index("SECOND")