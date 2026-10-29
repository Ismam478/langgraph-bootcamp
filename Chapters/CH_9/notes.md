# Ch 9: Messages and reducers

**What it does:** Shows how node outputs are merged into state, with and without reducers.
**When I'd use it:** Any state field that several nodes write to, such as chat messages or lists of results.
**One way it breaks:** Without a reducer, the latest write silently overwrites earlier ones. RemoveMessage then overwrites the entire list instead of deleting a specific message.

## Experiment A: no reducer
Code: `messages: list`
Output: `['']`
Why: Without a reducer, each node's return completely replaces the old list. "Iron Man" and "one" were lost because `delete_first` ran last and overwritten the whole state with `[RemoveMessage(...)]`, which prints as an empty string `''`.

## Experiment B: add_messages
Code: `Annotated[list, add_messages]`
Output: `['one', 'two']`
Why: `add_messages` appends new messages to the existing list using message IDs. When `RemoveMessage(id=...)` is passed, it searches the list for that specific ID and deletes the message ("Iron Man").

## Experiment C: Own Reducer
Code: `Annotated[list, own_reducer]`
Output: `['one', 'two']`
Why: Our custom reducer merges old and new lists while checking for `RemoveMessage`. If a `RemoveMessage` is received, it filters out the message with the matching ID and keeps the rest unique. If a message doesn't get an ID match, it won't be deleted.

## MessagesState
Same result as B. It is a prebuilt LangGraph state with a `messages` field that already uses `add_messages`.

## RemoveMessage
- **With a Reducer (`add_messages` / `own_reducer`):** Deletes the specific message matching the target ID, resulting in `['one', 'two']`.
- **Without a Reducer:** Replaces the entire state list with the `RemoveMessage` object itself, resulting in `['']`.

---

A reducer is a function that takes the existing state (`old`) and the incoming update (`new`) and returns a single merged value that becomes the new state.
Without one (Experiment A), the output was `['']`, because LangGraph defaults to key replacement, allowing the final `RemoveMessage` node to overwrite the entire message list.
With `add_messages` (Experiment B) the output was `['one', 'two']`.
This matters when several nodes write the same key, because without a reducer, each node's write will silently erase the work of previous nodes instead of combining them.