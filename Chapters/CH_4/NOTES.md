# Ch 4: LangGraph setup

**What it does:** Loads `.env` and checks the required variables, prints the langgraph version, exits with a clear error if something is missing.
**When I'd use it:** At the start of every project and every script, so a missing key fails fast with a readable message.

## Gate: fresh-clone test
- [ ] I cloned the repo into a NEW empty folder and followed ONLY the README.
- [ ] `uv run python -m Chapters.CH_4.check_status` passed.
