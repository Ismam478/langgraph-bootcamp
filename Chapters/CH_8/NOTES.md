# Ch 8: Pydantic schemas in graphs

**What it does:** Same idea as Ch 7 but the state is a Pydantic model, so bad input is rejected before any node runs.
**When I'd use it:** When input comes from outside (users, APIs) and must be checked.
**One way it breaks:** When the code gets a typo it breaks.

## Facts I verified by running it
- Inside a node the state is an OBJECT: `state.input_text`, not `state["input_text"]`.
- A `ValidationError` is raised by `invoke` before any node runs (see `tests/test_ch08_pydantic.py`).
- `@field_validator(..., mode="before")` runs before min/max length, so `"  a "` is stripped to `"a"` and then rejected as too short.

