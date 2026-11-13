# Ch 18: Memory (checkpointer + summary)
**What it does** : Has persistent SQLite memory on disk. Trims the older messages (if more than 6 messages) and summarizes for LLM to not lose its context.
**When I'd use it** : When I need to maintain the older message context for LLM.
**One way it breaks** : If its not orchestrated properly, it will fail to summarize. 

## Thread memory vs long-term memory
- Thread memory: Each chat session has its own thread id to remember the chat history. one thread's convo can't overlap with other threads.
- Long-term memory: Remembers only selective informations to personalize itself for the user.

## Demos (gate evidence)
### Two threads stay separate
| Thread | What I told it | What it answered later |
|---|---|---|
| a | Told My name | Remembers my name |
| b | Told few facts to remember | Remembers the facts perfectly |

### Stop the process, run again
- Prediction : If the state has more than 6 messages, It will create summary for the older texts and pass both the summary and query for LLM to Answer
- What it knew after restarting (recent messages, summary, or both): The summary wasn't avvailable at the first run, so it was able to recall the informations by looking at recent messages

## History and time travel
- What get_state_history returned for a 2-turn thread (prediction vs actual):
  - Prediction: expected 3 snapshots per turn. Correct
  - Actual: 3 snapshots per turn (message arrived, just before the LLM, after
    the answer). My print_history shows only 4 because it hides finished
    snapshots.
- Which checkpoint I chose and what I passed as input:
  - checkpoint_id 1f1df6da-f679-6dea-8000-c86aa723729e: turn 1, 1 message ("Hello, My name
    Is `...`"), next=chatbot. Passed in Input: None, with thread_id "a" + that checkpoint_id.
- What happened after the re-run (new branch or overwrite):
  - Predicted: a fresh reply to my first message. Correct.
  - New branch, no overwrite. The LLM answered again with different wording. The state now has
    only 2 messages, because the fork is the newest checkpoint and so the
    thread's head. My turn-2 conversation (the SQLite one) is still saved but
    is no longer part of the live state.

## Bugs I hit
- Summary stored as a list with the `add` reducer: It kept appending the latest summaries with the older ones.
- Changed the state type after data was saved: After changing the state type, I had to rerun the whole chatbot from beginning. 