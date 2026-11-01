# Chapter 14 — Parallel vs. Sequential Nodes

## 1. The Core Idea
* **What it does:** Runs multiple independent graph nodes at exactly the same time, instead of waiting for one to finish before starting the next.
* **When I'd use it:** When generating different formats of the same content or when fetching data from independent APIs where one request doesn't rely on the result of another.
* **One way it breaks:** If parallel nodes try to write strings or dictionaries to the exact same state key at the same time without an `Annotated` reducer, LangGraph throws an `InvalidUpdateError`.

## 2. The Aggregator & Edge Routing
Instead of hardcoding three separate edges:
`graph.add_edge('insta', 'aggregator')`
`graph.add_edge('linkedin', 'aggregator')`
`graph.add_edge('twitter', 'aggregator')`

Separate edges worked in my graph because all three branches are the same depth. They all finish in the same step.
`graph.add_edge(['insta', 'linkedin', 'twitter'], 'aggregator')`

## 3. The Same-Key Error (`research_results`)
* **Before (No Reducer):** When `research_results` was a plain `List[str]`, parallel nodes threw `InvalidUpdateError`. This happens because three nodes are trying to overwrite the exact same key in the state dictionary. 
* **Sequential Graph without Reducer:** If I run the sequential graph without a reducer, it *doesn't* break. Because the nodes run one after another, the state dictionary is updated sequentially. However, instead of appending, each node simply overwrites the previous node's string.
* **After (With Reducer):** By using `Annotated[List[str], add]`, it safely combine (append) the returns from the parallel nodes. 

*Note: For the aggregator, it is much safer to read from the individual keys (`state['insta']`) rather than the `research_results` list*

## 4. Timings: Parallel vs Sequential

| Graph Structure | Median Execution Time |
| :--- | :--- |
| **Parallel** | 10.01 s | 
| **Sequential** | 25.12 s | 

### The Gate Check: Why is parallel time equal to the slowest branch, not the sum?
When you run tasks in parallel, they all start at once. Instead of adding everyone's wait times together, the graph just waits for the slowest request to finish before moving on. Parallel Graph runs `(25.12/10.01) = ~2.5x` faster than the Sequential Graph. 