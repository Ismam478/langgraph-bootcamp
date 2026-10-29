from typing import Union, Literal
from Chapters.CH_6.llm import get_llm
from langchain_core.tools import tool, StructuredTool
from datetime import datetime
from context.dev import ContextDev
import os
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage

@tool
def calculator(operation: Literal["add", "subtract", "multiply", "divide"], a: Union[float, int], b: Union[float, int]) -> Union[float, int]:
    '''
    A simple calculator tool that performs basic arithmetic operations like addition, subtraction, multiplication, and division.
    '''
    print(">>> calculator is RUNNING")
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
def contextdev_search_tool(query: str) -> str:
    '''
    A tool that performs a search using the ContextDev API and returns the results.
    '''
    client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
    search = client.web.search(query=query, num_results=10)
    
    return search.results[0].description

clear_tools = [calculator, get_current_datetime, contextdev_search_tool]

vauge_descriptions = {
    "calculator": "Does Math.",
    "get_current_datetime": "return datetime",
    "contextdev_search_tool": "searches topics",
}
vauge_tools = [
    StructuredTool.from_function(func=t.func, name=t.name, description=vauge_descriptions[t.name])
    for t in clear_tools
]

tools_by_name = {tool.name: tool for tool in clear_tools}

def run_tool_call(call:dict):
    return tools_by_name[call["name"]].invoke(call["args"])

tools_llm = get_llm().bind_tools(clear_tools)

system_prompt = [SystemMessage(content="You are a helpful assistant. Dont try to make things on your own, use the tools to solve the problem. If you are unable to use the tools, say so.")]
messages = system_prompt.copy()
if __name__ == "__main__":

    response = tools_llm.invoke(system_prompt + [HumanMessage(content="What is 5 times 100? then divide by 20, then add 200.")])
    print("--- model has replied")
    print(f"Tool calls: {response.tool_calls}")

    messages.append(response)

    for call in response.tool_calls:
        result = run_tool_call(call)                                            
        print(f"ran {call['name']}({call['args']}) -> {result}")
        messages.append(ToolMessage(content=str(result), tool_call_id=call["id"]))
    
    print("final:", tools_llm.invoke(messages).content)