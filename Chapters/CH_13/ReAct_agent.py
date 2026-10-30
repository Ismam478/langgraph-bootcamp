from typing import Annotated, List, Literal, Union, TypedDict
from Chapters.CH_6.llm import get_llm
from langchain_core.tools import tool
from datetime import datetime
from context.dev import ContextDev
from operator import add
import os, json
from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.errors import GraphRecursionError
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END, add_messages


# Defining The State Graph
class graph_schema(TypedDict):
    messages : Annotated[List, add_messages]
    llm_calls : Annotated[int, add]
    input_tokens : Annotated[int, add]
    output_tokens : Annotated[int, add]


# Creating Custom Tools
@tool
def calculator(operation: Literal["add", "subtract", "multiply", "divide"], a: Union[float, int], b: Union[float, int]) -> Union[float, int]:
    '''
    A simple calculator tool that performs basic arithmetic operations like addition, subtraction, multiplication, and division.
    '''
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero.")
        return a / b

@tool
def get_current_datetime() -> str:
    '''
    A tool that returns the current date and time.
    '''
    return datetime.now().strftime("Current date: %Y-%m-%d, current time: %H:%M:%S")

@tool
def length_of_string(query: str) -> int:
    '''
    A tool that returns the length of a given string.
    '''
    return len(query)
       
@tool
def try_again() -> str:
    '''Always returns "try again". Keep calling it until it returns "done".'''
    return "try again"

@tool
def contextdev_search_tool(query: str) -> str:
    '''
    A tool that performs a search using the ContextDev API and returns the results.
    '''
    client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
    search = client.web.search(query=query, num_results=10)

    results = []
    for result in search.results:
        result = {
            "title": result.title,
            "description": result.description
        }
        results.append(result)
    
    return json.dumps(results[:3])


# Creating tool_box
tool_box = [calculator, get_current_datetime, contextdev_search_tool, length_of_string, try_again]

llm_with_tools = get_llm().bind_tools(tool_box)

# Creating the LLM Node
def llm_node(state:graph_schema):
    '''
    This is the LLM node, which takes the User query, invokes the LLM and returns the AIMessage generated from LLM.
    '''
    messages = state['messages']
    

    prompt = ChatPromptTemplate.from_messages([
        ('system', 'Imagine you are a helpful assistant, who uses only the provided tools to answer the user\'s question(dont try to find the answer on your own). Also dont make up answers, say "I dont Know" for the things you cannot answer'),
        # ('user', '{user_input}')
        MessagesPlaceholder(variable_name="messages")
    ])

    chain = prompt | llm_with_tools
    response = chain.invoke({'messages': messages})

    return {'messages': [response], 'llm_calls': 1, 'input_tokens': response.usage_metadata['input_tokens'] if response.usage_metadata else 0, 'output_tokens': response.usage_metadata['output_tokens'] if response.usage_metadata else 0}

# Creating the custom tool node for using the tool with loop
def custom_tool_node(state:graph_schema):
    '''
    This is the custom tool node, which takes the tool call from LLM and invokes the tool and returns the ToolMessage generated from the tool.
    '''

    last_message = state['messages'][-1]

    tools_by_name = {tool.name: tool for tool in tool_box}

    tool_results = []

    if last_message.tool_calls:
        for preferred_tool in last_message.tool_calls:
            tool_name = preferred_tool['name']
            tool_args = preferred_tool['args']
            tool_id = preferred_tool['id']
            try:
                selected_tool = tools_by_name[tool_name]
                tool_response = selected_tool.invoke(tool_args)

                tool_results.append(ToolMessage(content=tool_response, tool_call_id=tool_id))       

            except Exception as e:
                tool_results.append(ToolMessage(content=f"Error: {e}", tool_call_id=tool_id, status="error"))       
    return {'messages': tool_results}


# Creating the conditional edge loop
def if_tool_call(state:graph_schema):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        return 'tool_node'
    else:
        return 'end'


# Defining the state graph
graph = StateGraph(graph_schema)

graph.add_node('llm_node', llm_node)
graph.add_node('tool_node', custom_tool_node)

graph.add_edge(START, 'llm_node')
graph.add_conditional_edges('llm_node', if_tool_call, {'tool_node': 'tool_node', 'end': END})
graph.add_edge('tool_node', 'llm_node')


react_agent = graph.compile()

if __name__ == "__main__":
    # Saving the graph as a PNG or Mermaid file
    # from pathlib import Path

    # here = Path(__file__).parent
    # drawing = react_agent.get_graph()
    # try:
    #     (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
    #     print("Saved graph.png")
    # except Exception as e:
    #     (here / "graph.mmd").write_text(drawing.draw_mermaid())
    #     print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")

    # Invoking the ReAct agent with a sample query
    try:
        response = react_agent.invoke({'messages': [HumanMessage(content="divide 10 by 0")]}, config={"recursion_limit": 6})
        print(f"Final Response: {response['messages'][-1].content}")
        print(f"\n\n\n {response['messages']}")
        print(f"\n\n\n {response['llm_calls']}")
        print(f"\n\n\n {response['input_tokens']}")
        print(f"\n\n\n {response['output_tokens']}")
    except GraphRecursionError as e:
       print("Stopped by the safety limit:", e)
