# Chapter 13 — ReAct Agent from Scratch

## 1. What I built
I built a custom LangGraph ReAct agent from scratch, manually wiring the nodes to see exactly how data moves. It includes tools for math, time, string length, web searches, and testing infinite loops.

**Graph:** START → llm_node → (tool_node → llm_node)* → END


## 2. How the loop works (my words)
- What the model does vs what my code does: It reads the conversation and decides whether to answer directly or ask for a tool. It generates the tool and args it needs and my code triggers the Python functions, catches the output, and feeds it back to the model.
- Why the AIMessage must stay in the message list: If we drop the AI's tool request from the history, the model forgets why the tool was run in the first place.
- What `if_tool_call` checks, and what happens when it's false: If the last message from `messages` does not contain any tool call information, It ends the Loop.

## 3. Task 2: Runaway loop
- Prompt used: "Call try_again until it returns done"
- `recursion_limit`: 6 Times
- `Prediction`: I figured it would keep running forever until my API budget ran dry.
- `Actual`: 6 LLM calls, 5 tool runs (then it safely crashed)
- Why the numbers match / don't match: It hit the safety limit. LangGraph's recursion limit stepped in and killed the loop at step 6 because the tool kept blindly returning "try again".
- Recursion error vs tool error (who is at fault, how I handle each): Recursion Error usually happens for a bad prompt or bad agent design so I can handle it with a hard config limit. A tool error is an actual Python code crash and I can handle it by catching the exception inside the node and feeding it back to the LLM.

## 4. Task 3: Tool error handling
| | Before (no try/except) | After (per-call try/except) |
|---|---|---|
| What I saw | The whole script blew up with a Python traceback | The script finished perfectly. The error was caught silently |
| What the user would see | A broken app or a 500 server error screen | A polite message explaining that you can't divide by zero |
| What the model did next | Nothing, the program died before it could even try | It read the error string in the state, realized the math failed, and wrote a good response |

## 5. Custom nodes vs `ToolNode`
- Jobs `ToolNode` took over from my code: It automatically loops through the requested tools, runs the functions, and wraps the outputs in ToolMessage
- Default behaviour on a tool error (my prediction → what happened): I guessed it might handle them, but without extra setup, it often just lets the Python exception crash the whole chain.
- With `handle_tool_errors`: It catches the crash and sends a generic "tool failed" message back to the model.
- Error text: mine vs ToolNode's, which helps the model more? Mine is way better. Instead of a generic error, I can pass the exact exception text (like `ValueError: Cannot divide by zero`) straight to the model so it actually knows how to fix its mistake.
- What I'd choose in a real project, and why: Custom node, hands down. I need total control to run tools concurrently (like with `asyncio.gather`), add human approval steps before dangerous tools run, and handle errors my specific way.
