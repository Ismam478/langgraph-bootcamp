from operator import add
from typing import Annotated, List, TypedDict
from Chapters.CH_6.llm import get_llm
from pydantic import BaseModel, Field
from langgraph.types import Send
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END
import time

MAX_TASKS = 6 

# Function to clean the list of tasks
def clean_tasks(raw_tasks: List[str], query: str) -> List[str]:
    """
    This function cleans the list of tasks by removing duplicates and limiting the number of tasks to MAX_TASKS.
    If no tasks are identified, it returns the original query as a single task.
    """
    tasks = [t.strip() for t in raw_tasks if t.strip()]
    tasks = list(dict.fromkeys(tasks))[:MAX_TASKS]
    if not tasks:
        tasks = [query]
    return tasks

# Orchestrator Workflow Graph Schema
class GraphSchema(BaseModel):
    query : str = Field(description="The query to be executed by orchestrator node.")
    tasks: List[str] = Field(description="The list of tasks to be executed by worker nodes", default=[])
    results: Annotated[List[dict], add] = Field(description="The list of index and results from the worker nodes", default=[])
    summary: str = Field(description="The summary of all the task result according to the user query", default="")
    llm_calls: Annotated[int, add] = Field(description="The number of LLM calls made by the orchestrator node", default=0)

# LLM Schema for Orchestrator Node (for structured output)
class LLMSchema(BaseModel):
    tasks: List[str] = Field(description="The list of tasks to be executed by worker nodes", default=[])

# Worker Schema for Worker Node
class WorkerSchema(TypedDict):
    task: str
    index: int
    query : str


# Orchestrator Workflow Graph Nodes
def orchestrator_node(state: GraphSchema) -> dict:
    """
    This function receives the user query and identifies each single task from the query.
    """
    query = state.query

    orchestrator_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are the Orchestrator Node for a parallel execution system. 
        Your sole objective is to decompose a composite user query into a list of independent, self-contained tasks that can be executed concurrently by worker nodes.

        CRITICAL RULES:
        1. **Task Isolation:** Each task must be fully self-contained. Do not split a single logical query into sequential sub-steps (e.g., "Find X" and "Analyze X" should be one task: "Find and analyze X").
        2. **Hard Cap (Maximum 6 Tasks):** You must return between 1 and 6 tasks. If a user asks for more than 6 distinct items, group related items together logically to stay at or below the 6-task limit.
        3. **No Synthesis or Formatting:** NEVER create tasks for aggregating, summarizing, or formatting the final output. A downstream Collector node automatically handles all synthesis.
        4. **Literal Extraction:** Extract only what is explicitly requested. Do not invent supplementary tasks."""),
        
        ("user", "USER QUERY: {user_query}\n\nDecompose this query into a list of tasks following the critical rules.")
    ])

    llm = get_llm().with_structured_output(LLMSchema)
    
    try: 
        chain = orchestrator_prompt | llm 
        tasks = chain.invoke({'user_query': query}).tasks
    except Exception as e:
        print(f"Error in orchestrator_node: {e}")
        tasks = []

    tasks = clean_tasks(tasks, query)
    print(f"\n\nThe length of tasks is {len(tasks)}")

    for i, t in enumerate(tasks):
        print(f"Task-{i+1}: {t}")

    return {'tasks': tasks, 'llm_calls': 1}  

# Function to assign tasks to worker nodes (Using Send objects)
def assign_workers(state: GraphSchema):
    """
    This function assigns the tasks to the worker nodes and returns a list of Send objects, each containing the task and its index.
    """
    return [Send('worker_node', {'task': t, 'index': i, 'query': state.query})
            for i, t in enumerate(state.tasks)
        ]

# Worker Node (Executes each task independently and returns the result along with the index)
def worker_node(state: WorkerSchema) -> dict:
    """
    This function executes the task assigned to the worker node and returns the result along with the index
    """
    task = state['task']
    index = state['index']
    query = state['query']

    t0 = time.perf_counter()

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a worker node, who recieves the task and executes it according to the user query'),
            ('user', "This is the Task: {task} and query: {query}. I want you to execute the task and return the result")
        ]
    )
    llm = get_llm()
    chain = prompt | llm 
    result = chain.invoke({'task': task, 'query': query}).content
    
    t1 = time.perf_counter()
    print(f"Worker node {index} executed task in {t1-t0:.1f}s")

    return {'results': [{'index': index, 'result': result}], 'llm_calls': 1}

# Collector Node (Collects the results and summarizes them according to the user query)
def collector_node(state: GraphSchema) -> dict:
    """
    This function collects the results from the worker nodes, orders them according to their index, and summarizes them based on the original user query. 
    """
    
    ordered_results = [r["result"] for r in sorted(state.results, key=lambda r: r["index"])]
    query = state.query
    llm_calls = state.llm_calls

    t0 = time.perf_counter()

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a collector node, who recieves the results from the worker nodes and summarizes them according to the user query'),
            ('user', "These are the results from the worker nodes {results}. I want you to summarize them according to the user query: {user_query}")
        ]
    )
    llm = get_llm()
    chain = prompt | llm
    summary = chain.invoke({'results': ordered_results, 'user_query': query}).content

    t1 = time.perf_counter()
    print(f"Collector node executed in {t1-t0:.1f}s")

    print(f"Total LLM calls made by the orchestrator node: {llm_calls + 1}") # +1 for the collector node


    return {'summary': summary, 'llm_calls': 1}

graph = StateGraph(GraphSchema)
graph.add_node('orchestrator_node', orchestrator_node)
graph.add_node('worker_node', worker_node)
graph.add_node('collector_node', collector_node)

graph.add_edge(START, 'orchestrator_node')
graph.add_conditional_edges('orchestrator_node', assign_workers, ['worker_node'])
graph.add_edge('worker_node', 'collector_node')
graph.add_edge('collector_node', END)

orchestrator_workflow = graph.compile()

if __name__ == '__main__':
    #### Saving the graph as a PNG or Mermaid file
    from pathlib import Path

    here = Path(__file__).parent
    drawing = orchestrator_workflow.get_graph()
    try:
        (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
        print("Saved graph.png")
    except Exception as e:
        (here / "graph.mmd").write_text(drawing.draw_mermaid())
        print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")


    for q in ["How does a bicycle work?",
            "Compare the economic, health and education impacts of AI in Bangladesh"]:
        t0 = time.perf_counter()
        workers = 0
        for chunk in orchestrator_workflow.stream({"query": q}, stream_mode="updates"):
            if "worker_node" in chunk:
                workers += 1
        print(f"{q!r}: N={workers}, {time.perf_counter()-t0:.1f}s")