import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

import Chapters.CH_19.HumanInTheLoop as hitl


class FakeLLM(RunnableLambda):
    """Fake model: returns 'draft 1', 'draft 2', ... and records every prompt it was given."""
    def __init__(self):
        seen = []
        def fn(prompt_value):
            seen.append(prompt_value.to_string())
            return AIMessage(content=f"draft {len(seen)}")
        super().__init__(fn)
        object.__setattr__(self, "seen", seen)


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Fake model + output file in a temp folder, so tests never call the API or touch real files."""
    fake = FakeLLM()
    out = tmp_path / "email_draft.txt"
    monkeypatch.setattr(hitl, "get_llm", lambda *a, **k: fake)
    monkeypatch.setattr(hitl, "OUTPUT_FILE", out)
    return fake, out


def cfg(thread="t1"):
    return {"configurable": {"thread_id": thread}}


def start(app, config, topic="project update"):
    return app.invoke({"topic": topic}, config)


def test_graph_pauses_after_draft_and_writes_nothing(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    result = start(app, cfg())

    assert result["__interrupt__"][0].value == {"draft": "draft 1"}
    assert app.get_state(cfg()).next == ("approval",)
    assert not out.exists()          # nothing is saved before approval


def test_approve_writes_the_draft(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    result = app.invoke(Command(resume={"action": "approve"}), cfg())

    assert "__interrupt__" not in result
    assert "draft 1" in out.read_text()

def test_edit_writes_humans_text_not_the_models(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    app.invoke(Command(resume={"action": "edit", "text": "my own words"}), cfg())

    text = out.read_text()
    assert "my own words" in text
    assert "draft 1" not in text


def test_reject_redrafts_with_feedback_and_pauses_again(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    result = app.invoke(Command(resume={"action": "reject", "feedback": "make it shorter"}), cfg())

    assert result["__interrupt__"][0].value == {"draft": "draft 2"}
    assert "make it shorter" in fake.seen[1]
    assert "draft 1" in fake.seen[1]
    assert not out.exists()

def test_feedback_is_cleared_after_redraft(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    app.invoke(Command(resume={"action": "reject", "feedback": "make it shorter"}), cfg())
    assert app.get_state(cfg()).values["feedback"] == "" 

def test_reject_then_approve_saves_only_the_final_draft(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    app.invoke(Command(resume={"action": "reject", "feedback": "shorter"}), cfg())
    app.invoke(Command(resume={"action": "approve"}), cfg())

    text = out.read_text()
    assert "draft 2" in text
    assert "draft 1" not in text


def test_unknown_action_raises(env):
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg())
    with pytest.raises(ValueError, match="Unknown Action"):
        app.invoke(Command(resume={"action": "banana"}), cfg())


def test_two_threads_do_not_mix(env):
    fake, out = env
    app = hitl.builder.compile(checkpointer=InMemorySaver())
    start(app, cfg("a"), topic="topic A")
    start(app, cfg("b"), topic="topic B")
    app.invoke(Command(resume={"action": "approve"}), cfg("a"))

    assert app.get_state(cfg("a")).next == ()
    assert app.get_state(cfg("b")).next == ("approval",)      


def test_resume_from_a_new_saver_object(env, tmp_path):
    fake, out = env
    db = str(tmp_path / "ck.sqlite")

    with SqliteSaver.from_conn_string(db) as saver1:           
        start(hitl.builder.compile(checkpointer=saver1), cfg())

    with SqliteSaver.from_conn_string(db) as saver2:           
        app2 = hitl.builder.compile(checkpointer=saver2)
        state = app2.get_state(cfg())
        assert state.tasks[0].interrupts[0].value == {"draft": "draft 1"}
        app2.invoke(Command(resume={"action": "approve"}), cfg())

    assert "draft 1" in out.read_text()