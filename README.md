# LangGraph Bootcamp

My hands-on learning repo for **LangGraph and agentic AI**. I followed a video course chapter by chapter, built each exercise myself, wrote notes with evidence from real runs, and added tests. The goal is a **Support Triage Assistant** capstone, which I'll use as the base for freelance AI-agent work.

## What I can build now

| Skill | Where |
|---|---|
| State graphs (TypedDict and Pydantic), reducers | Ch 7-9 |
| Chatbots, message trimming, prompt templates | Ch 10-11 |
| Tool calling and a ReAct agent built from scratch (loop limit, tool-error handling, token counter) | Ch 12-13 |
| Workflows: parallelization, routing, orchestrator-worker (`Send`), generator-evaluator | Ch 14-17 |
| Memory: summaries, SQLite checkpoints, time travel | Ch 18 |
| Human-in-the-loop: `interrupt`, `Command`, approve/edit/reject, resume in a new process | Ch 19 |
| Testing LLM apps with fake models (pytest, no API calls) | `tests/` |

## Capstone: Support Triage Assistant (in progress)

A customer email goes in, and a human-approved reply comes out.

```
email -> router -> specialist agent (tools) -> draft reply -> human approval -> send -> log
```

- **Router:** structured output picks the category (billing, bug, order status, other) and urgency
- **Specialists:** small ReAct agents with mock lookup tools (order, customer) and an FAQ search
- **Draft:** length and keyword rules are checked in Python; the model only judges tone
- **Approval:** the graph pauses; a human can approve, edit, or reject with feedback (max 2 redrafts)
- **Memory:** one thread per customer, stored in SQLite
- **Safety:** recursion limit, loop cap, token counter per ticket
- **Evidence:** a 15-email test set with measured routing accuracy, plus pytest tests with a fake model

## Tech stack

- Python 3.12+, [uv](https://docs.astral.sh/uv/)
- LangGraph, LangChain, `langchain-openai`
- SQLite (`langgraph-checkpoint-sqlite`)
- pytest

## Setup

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/).
2. Clone and install:

   ```bash
   git clone https://github.com/Ismam478/langgraph-bootcamp.git
   cd langgraph-bootcamp
   uv sync
   ```

3. Create your environment file:

   ```bash
   cp .env.example .env
   ```

   Fill in `.env`:

   ```
   OPENAI_API_KEY=your-key-here
   AI_MODEL=gpt-5-nano
   PROVIDER=openai
   CONTEXT_DEV_API_KEY=your-key-here   # only needed for the web-search tool in Ch 13
   ```

   `.env` is git-ignored, so keys are never committed.

4. Check the setup:

   ```bash
   uv run python -m Chapters.CH_4.check_status
   ```

## Run things

Run scripts as modules from the repo root, because chapters import each other:

```bash
uv run python -m Chapters.CH_13.ReAct_agent
uv run python -m Chapters.CH_19.HumanInTheLoop            # full approval loop
uv run python -m Chapters.CH_19.HumanInTheLoop start      # draft, pause, exit
uv run python -m Chapters.CH_19.HumanInTheLoop resume     # new process, continue from the pause
```

Run the tests (no API key, no cost; the model is faked):

```bash
uv run pytest
```

Running a chapter script makes real API calls, which cost a small amount of money.

## Project structure

```
Chapters/
  CH_4  - CH_6    setup, OpenAI calls and cost, get_llm() helper
  CH_7  - CH_9    state graphs, Pydantic state, messages and reducers
  CH_10 - CH_12   chatbots, prompt templates, tools
  CH_13           ReAct agent from scratch
  CH_14 - CH_17   parallelization, routing (with eval set), orchestrator-worker, generator-evaluator
  CH_18           memory and SQLite checkpoints
  CH_19           human-in-the-loop email approval
tests/            pytest tests with fake models
LEARNING_LOG.md   skills, lessons and progress
```

Each chapter folder has a `Notes.md` with what I built, how it works in my words, and evidence from real runs.

## Progress

| Chapter | Topic | Status |
|---|---|---|
| 1-9 | Setup, API and cost, state graphs, Pydantic, reducers | Done |
| 10-12 | Chatbots, prompt templates, tools | Done |
| 13 | ReAct agent from scratch | Done |
| 14-17 | Parallelization, routing, orchestrator-worker, generator-evaluator | Done |
| 18 | Memory and checkpoints | Done |
| 19 | Human-in-the-loop | Done |
| Capstone | Support Triage Assistant | In progress |

## Lessons that stuck

- A node returns only the keys it changes; reducers decide how updates merge.
- Put rules you can check in Python (word count, keywords) and use the model only for judgement.
- A tool error should become a message the model can read, not a crash.
- `interrupt()` re-runs its node from the first line on resume, so side effects go in a separate node after approval.
- Test with fake models: no cost, no flakiness, and you can inspect exactly what the model was sent.
- Predict before you run, then compare. The gap is where the learning is.