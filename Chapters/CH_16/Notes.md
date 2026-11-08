# Ch 16: Orchestrator-Worker
**What it does** : Creates list of task according to the user's query and Send launches each task with a worker node
**When I'd use it** : When I will need worker nodes to work `N` times, I will use it.
**One way it breaks** : If there is any error with worker node's name in the the conditional logic.

## How Send works 
- What `Send(node, arg)` creates, and what the worker receives: Creates SEND object and it passes the worker node and the args for worker node
- Why the worker needs its own state and why `completed results` needs a reducer: The worker needs its isolated state to independently process its assigned chunk without locking or unnecessarily modifying the global graph state and without a reducer, LangGraph's default behavior would simply overwrite the key with the last worker's output.

## Prediction vs actual
| Check | Prediction | Actual |
|---|---|---|
| Raw N, bicycle query | 2 | 5 |
| Raw N, Bangladesh query | 4 | 3 |

## Two runs, different N (the gate evidence)
| Query | N | LLM calls | Total time | Slowest worker |
|---|---|---|---|---|
| `How does a bicycle work?` | 5 | 7 | 36.6s | 19.0s |
| `Compare the economic, health and education impacts of AI in Bangladesh` | 3 | 5 | 51.5s | 26.4s |

## The planner is unreliable
- Raw N across runs for the same query: LLM get different `N` each time it runs
- What the cap and fallback protect against, and what the cap loses silently: Strips off empty tasks list, whitespaces and if the tasks variable is empty, the whole query will be passed as task. If the planner returns 10 tasks, it takes the first 6 and ignores the last 4 because of the cap.

## Prompt change
- Before / after and the effect: Before, It used to generate random N workers. After setting the upper limit, LLM generates at most 6 Workers. (Before-> 9 workers, after-> 1-6 workers)

## Gate
- How this differs from Ch 14 (build time vs run time): Chapter 14 had constant 3 workers (Decided while building), but Chapter 16 can create its own `N` number of workers(Decided while runtime).