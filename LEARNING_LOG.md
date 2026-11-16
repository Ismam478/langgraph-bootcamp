# Learning Log

## What I can already do
- Python, SQL
- LangChain, RAG
- Semantic / recursive / parent-document chunking
- Hybrid search (BM25 + dense vectors), reranking (cross-encoders, Cohere Rerank)
- HyDE, multi-query, query routing

## What I learned in this bootcamp (LangGraph)
- **Graphs:** StateGraph, TypedDict vs Pydantic state, reducers (`add`, `add_messages`), conditional edges
- **Agents:** tool calling, ReAct loop built by hand, `recursion_limit`, per-call tool error handling, `ToolNode` vs custom node vs `create_agent`
- **Workflows:** parallelization, routing with an eval set, orchestrator-worker with `Send`, generator-evaluator loop with an iteration cap
- **Memory:** message summarization, `SqliteSaver`, thread separation, time travel (replay vs fork)
- **Human-in-the-loop:** `interrupt`, `Command(resume=...)`, `Command(goto, update)`, resuming from a different process
- **Testing:** pytest with fake models, temp files and temp databases, mutation checks (break the code on purpose and confirm a test fails)

## Habits I'm building
- Predict the result before running, then compare
- Rules in Python, judgement in the model
- No API calls or database writes at import time
- Every chapter ends with a Notes file: what it does, when I'd use it, one way it breaks, plus evidence from real runs

## Mistakes worth remembering
- Returning `Command(resume=...)` from a node instead of passing it to `invoke`
- Forgetting `thread_id` when using a checkpointer
- Putting rules inside the model prompt and getting inconsistent results
- Changing a state type and breaking old saved threads

## Capstone: Support Triage Assistant
Customer email -> router -> specialist agent with tools -> draft reply -> human approval -> send -> log.

Checklist:
- [ ] State, mock data and lookup tools, with tests
- [ ] Router (category and urgency) and a 15-email accuracy check
- [ ] One specialist end to end, then the others
- [ ] Drafter with Python rules, then human approval (approve / edit / reject)
- [ ] Memory per customer, recursion limit, redraft cap, token counter
- [ ] Tests with fake models
- [ ] README with diagram, results table and demo

## After the capstone
- Write a one-page case study (problem, design, results, what I'd improve)
- Apply for freelance AI-agent jobs using the capstone as the portfolio piece