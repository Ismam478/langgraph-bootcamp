# Ch 17: Generator-Evaluator
**What it does** : Takes user query and Evaluates until it has the correct informations for the user query.
**When I'd use it** : When users would need answers containing only the relevant topics.
**One way it breaks** : If the prompt isn't written correctly, it won't be able to evaluate the user query perfectly.

## Who checks which rule
| Rule | Checked by (Python / model) | Why |
|---|---|---|
| 40-60 words | Python | LLM's might hallucinate while counting words |
| 3 required keywords | Python | Exact string check in `check_rules`; I pass the keywords into the state myself |
| Friendly tone | Model | Python cannot judge tone |

## Run 1: improves across iterations
- Prediction (BEFORE running):
- Query: "Write a product description for a water bottle. include the keywords insulated, leak-proof, lightweight, and be friendly" (word limit left out on purpose)
| Iteration | Word count | Missing keywords | Tone ok | Passed | Feedback sent to generator |
|---|---|---|---|---|---|
| 1 | 161 | none | not checked (failed in Python first) | No | Outside the 40-60 word limit |
| 2 | 44 | none | Yes | Yes | Approved |

## Run 2: the cap stops the loop
- The impossible rule I added on purpose: 
- Prediction (iterations before stopping):
- Actual: 3 iterations, then it stopped
| Iteration | Passed | Why it failed |
|---|---|---|
| 1 | No | 42 words, outside the allowed range |
| 2 | No | 41 words, outside the allowed range |
| 3 | No | 47 words, outside the allowed range |

## What goes wrong without the cap
- The evaluator will keep on running until the evaluation passes (I might fall into an infinite loop)

## Bugs I hit
- Counter never incremented (the cap never fired): what I saw: with a fake evaluator that always said "no", the loop only stopped at a recursion limit of over 10,000 steps (measured by me with a fake model, not on the real API)
- Off-by-one in the cap (4 generations instead of 3): the first working counter allowed 4 generations (fake-model test)
- Counter doubled because I returned `iteration + 1` with an `add` reducer: the counter read 1, 3, 7 after three loops instead of 1, 2, 3
- Asked the model to count words: LLM's are not fit enought to count the words, it hallucitanes with word counting.