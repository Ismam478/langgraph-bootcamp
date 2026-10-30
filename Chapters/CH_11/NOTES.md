# Ch 11: Prompt templates

**What it does:** All prompt text lives in `prompts.py` (`ChatPromptTemplate` with `{tone}` and `{audience}`); the graph code never mentions it.
**When I'd use it:** When behaviour must be changed or tested without touching logic.
**One way it breaks:** If the `{tone}` and `{audience}` never gets initialized, the prompt will not work

## Gate: behaviour changes with zero edits to graph code (`python -m Chapters.CH_11.tone_demo`)

- friendly reply: `AI: Hi there! I’m here and ready to help. How can I assist you today?`
- formal reply: `AI: Good day, sir. I trust you are well and in high spirits. It is a privilege to make your acquaintance. How may I assist you today?`
- [ ] `uv run pytest tests/test_ch11_prompts.py` passes (no LLM call needed).
