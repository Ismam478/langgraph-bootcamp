# Ch 9: Messages and reducers

**What it does:** Shows how node outputs are merged into state, with and without reducers.
**When I'd use it:** Any state field that several nodes write to, such as chat messages or lists of results.
**One way it breaks:** Without a reducer, the latest write silently overwrites earlier ones. RemoveMessage then does not delete anything.

## Experiment A: no reducer
Code: `messages: list`
Output: `['two']`
Why: Each node's return replaces the old value. "Iron Man" and "one" were lost.

## Experiment B: add_messages
Code: `Annotated[list, add_messages]`
Output: `['Iron Man', 'one', 'two']`
Why: The reducer appends the new messages to the old ones.

## Experiment C: Own Reducer
Code: `Annotated[list, own_reducer]`
Output: `['Iron Man', 'one', 'two', '']`
Why: The reducer appends the new messages to the old ones, also I have total control over the messages.

## MessagesState
Same result as B. It is a prebuilt state with a `messages` field that already uses add_messages.

## RemoveMessage
- With add_messages: the first message was deleted, result `['one', 'two']`.
- Without a reducer: result `['']`. Message ids were never assigned, so id=None,
  and the RemoveMessage object replaced the whole list.