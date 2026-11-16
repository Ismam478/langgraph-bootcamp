# Ch 19: Human-in-the-Loop (email approval)
**What it does** : It drafts an email according to the user's topic and waits for human approval before saving it (saving to a file stands in for sending, for prototyping). The human can approve, reject with feedback (it redrafts), or edit the text.
**When I'd use it** : Whenever an action is critical or irreversible (finance, legal, customer-facing messages) and a person must approve it before it happens.
**One way it breaks** : If I invoke without a `thread_id` (or without a checkpointer), the graph has nowhere to save the paused state, so it crashes and can't be resumed.

## How interrupt and Command work (my words)
- What `interrupt(value)` does: It pauses the graph at that line and saves the state with the checkpointer. The `value` goes out to my script through `invoke`, where it appears under `__interrupt__`, so my script knows it is paused and what to show the person.
- What `Command(resume=...)` becomes inside the node: I pass it to `invoke` (not return it from a node). Whatever I give it becomes the return value of `interrupt(...)` inside the node, so the human's decision gets into the graph. It does not stop the graph; it continues it.
- What `Command(goto=..., update=...)` does: A node returns it. `goto` chooses which node runs next, and `update` changes values in the state before that node runs.
- Why `input()` must not be inside a node: A node waiting on `input()` blocks the whole run and ties it to one live terminal. The pause/resume design needs the answer to arrive through `Command(resume=...)`, so the process can stop after the pause and a fresh process can resume later. So `input()` belongs in the script that drives the graph.
- What happens to code before `interrupt` when the graph resumes: The node runs again from its first line. Anything before `interrupt` runs twice (once at the pause, once at the resume), so side effects such as writing a file must live in a separate node after the approval.

## The decision payload
| Action | What I send | Where the node goes next | What changes in state |
|---|---|---|---|
| approve | {"action": "approve"} | write | nothing |
| edit | {"action": "edit", "text": "..."} | write | results = the human's text |
| reject | {"action": "reject", "feedback": "..."} | draft | feedback = the human's reason |
| anything else | | raises ValueError | |

## Demos 
- Reject then approve (one run):
  - Topic: absence for illness. First draft pause, then reject with "make it a little formal".
  - The second draft became more formal (changed the closing to "Sincerely"), the graph paused again, and I approved. The email was saved.
  - Earlier run: rejected twice ("I will be back on 19 Nov 2026, also add my name", then "add supervisor's name"). Both pieces of feedback appeared in the next draft.
- Edit transcript: The original draft from the LLM was overwritten with my text, and the file contained exactly my text.
- Cross-process: Process 1: `python -m Chapters.CH_19.HumanInTheLoop start`, topic "Need three days leave"; it printed "Paused for next Invocation" and exited. Process 2 (a new run): `... resume`; it showed the saved draft ("Request for three days' leave"), I approved, and it printed "Email Saved Successfully".

## Bugs I hit
- Returned `Command(resume=True)` from a node: approving silently ended the graph without writing the email.
- `invoke` without a `thread_id`: crashed because the checkpointer needs one.
- `ask_human` branches for approve and reject had no `return`: it looped asking forever.
- `feedback` was not cleared after use: the next email on the same thread was a revision of the old one.
- Typing a sentence instead of approve/reject/edit: the script printed "Please type approve, reject or edit." and showed the draft again.

## Gate
- All three paths (approve, edit, reject) pass tests, and the cross-process resume works: 8 tests pass, and the demo above ran in two separate processes.