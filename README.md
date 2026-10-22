# LangGraph Bootcamp

My hands-on learning repo for **LangGraph and agentic AI**. I follow a video course chapter by chapter, pause after each section, and build the exercises myself. The goal is to build a **Support Triage Assistant** as a capstone and use it as the base for freelance AI-agent work.

## What I'm building toward

**Support Triage Assistant** (capstone, after Chapter 19):

- A router sends each customer message to billing, tech or general
- A specialist node uses tools (a fake order lookup, plus RAG over a small FAQ)
- The assistant drafts a reply, then pauses for human approval
- Memory keeps each customer's thread
- Loop limit, token counter, and a 15-question test set with a measured accuracy

## Tech stack

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management
- LangGraph, LangChain, `langchain-openai`
- OpenAI API (default model set in `.env`)

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

   Then open `.env` and fill in:

   ```
   OPENAI_API_KEY=your-key-here
   AI_MODEL=gpt-5-nano
   PROVIDER=openai
   ```

   `.env` is git-ignored, so your key never gets committed.

4. Check that the setup works:

   ```bash
   uv run python -m Chapters.CH_4.check_status
   ```

   You should see that the required environment variables are loaded.

## How to run a chapter

Run scripts as modules from the repo root, because chapters import each other:

```bash
uv run python -m Chapters.CH_7.first_graph
```

Note: running a chapter makes real API calls, which cost a small amount of money.

## Project structure

```
Chapters/
  CH_4/   environment check (check_status.py)
  CH_5/   OpenAI API calls, token usage, cost estimate
  CH_6/   get_llm() helper
  CH_7/   first state graph (TypedDict state)
  CH_8/   state graph with a Pydantic state
  CH_9/   messages and reducers
LEARNING_LOG.md   skills, goals and progress tracker
```

## Progress

| Chapter | Topic | Status |
|---------|-------|--------|
| 1 | Introduction | Done |
| 4 | LangGraph setup | In progress (fixing error handling) |
| 5 | OpenAI API and cost | In progress |
| 6 | Connecting to LLMs | In progress |
| 7 | First state graph | Redoing with conditional edges |
| 8 | Pydantic schemas in graphs | In progress |
| 9 | Messages and reducers | In progress |
| 10-19 | Chatbot, tools, ReAct, workflows, memory, human-in-the-loop | Not started |
| Capstone | Support Triage Assistant | Not started |

Detailed notes are in [LEARNING_LOG.md](LEARNING_LOG.md).

## What I've learned so far

- Setting up a LangGraph project with environment variables
- Estimating LLM cost from token usage
- Building state graphs with TypedDict and Pydantic state
- Using reducers to combine values written by different nodes

## Next steps

- Conditional edges and tests for each graph path
- Provider-independent `get_llm()` driven by `.env`
- Tool binding and a ReAct agent from scratch