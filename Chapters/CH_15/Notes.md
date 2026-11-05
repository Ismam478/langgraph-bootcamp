# Ch 15: Routing Workflow
**What it does:** Takes query from user and decides which node it should go and execute the task.
**When I'd use it:** When I will have choose between two or more other type of task from the query.
**One way it breaks:** If the graph has any faulty node.

## Design
- The 3 categories and my one-line definition of each: 
                                                    1. `Billing` means Queries related to money, invoices, subscriptions, payments, or refunds"
                                                    2. `Tech` means Queries related to bugs, errors, system outages, login issues, or how to use a specific software feature" 
                                                    3. `General` means Anything else that doesn't fit into billing or technical support. This could be questions about company policy, opening hours, business inquiries, or general feedback"


## Prediction vs actual
| Check | Prediction | Actual |
|---|---|---|
| Prompt V1 | 13/15 | 15/15 |
| Hard set V1 | 8/10 | 9/10 |
| Prompt V2 (evaluated_prompt) | 15/15 | 15/15 |
| Hard set V2 (evaluated_prompt) | 9/10 | 10/10 |

## Results v1 (`results_v1.json`)
- Overall / per category / tricky: `100%` / {`Billing: 5/5,    Tech: 5/5,    General: 5/5`} / `3/3`
- Mistakes: None

## Results v1 (`results_hard_v1.json`)
- Overall / per category / tricky: `90%` / {`Billing: 3/3`,    `Tech: 3/4`,    `General: 3/3`} / `6/7`
- Mistakes: [
    `Query` = Where do I click to update my credit card on the website?,
    `Reason` = The prompt has no rule for what to do when both `Billing` and `Tech` apply. That makes this a missing tie-break rule. It’s also an arguable label.
]

- Prompt_V2 = It has Prompt_V1 + A Tie Break (Imagining this code will be using for Tech Company policies) [I wrote V2 after seeing the failure]
## Results v2 (`results_v2.json`)
- Overall / per category / tricky: `100%` / {`Billing: 5/5`,    `Tech: 5/5`,    `General: 5/5`} / `3/3`
- Mistakes: None

## Results v2 (`results_hard_v2.json`)
- Overall / per category / tricky: `100%` / {`Billing: 3/3`,    `Tech: 4/4`,    `General: 3/3`} / `7/7`
- Mistakes: None


## Failure analysis (from `results_hard_v1.json`)
| Query | Expected → predicted | Arguable label / missing rule / model mistake |
|---|---|---|
| Query → 9 | `tech` → `billing` | `Arguable label + missing rule` |

## Gate
- Accuracy number: `100%` (The prompt was evaluated imagining the code will be using for Tech company policies)