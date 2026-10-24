from typing import Union, Literal
from Chapters.CH_6.llm import get_llm
from langchain.tools import tool
from datetime import datetime
from context.dev import ContextDev
import os
from langchain_core.messages import SystemMessage, HumanMessage

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
def contextdev_search_tool(query: str) -> str:
    '''
    A tool that performs a search using the ContextDev API and returns the results.
    '''
    client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
    search = client.web.search(query=query, num_results=10)
    
    return search.results

# Vauge Docstrings
@tool
def calculator_2(operation: Literal["add", "subtract", "multiply", "divide"], a: Union[float, int], b: Union[float, int]) -> Union[float, int]:
    '''
    Does Math.
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
def get_current_datetime_2() -> str:
    '''
    return datetime
    '''
    return datetime.now().strftime("Current date: %Y-%m-%d, current time: %H:%M:%S")
       

@tool
def contextdev_search_tool_2(query: str) -> str:
    '''
    searches topics
    '''
    client = ContextDev(api_key=os.environ["CONTEXT_DEV_API_KEY"])
    search = client.web.search(query=query, num_results=10)
    
    return search.results

tool_box = [calculator, get_current_datetime, contextdev_search_tool, calculator_2, get_current_datetime_2, contextdev_search_tool_2]
tools_llm = get_llm().bind_tools(tool_box)

if __name__ == "__main__":
    response = tools_llm.invoke([SystemMessage(content="You are a helpful assistant. Dont try to make things on your own, use the tools to solve the problem. If you are unable to use the tools, say so."), HumanMessage(content="What is 5 times 100?")])
    print(response.tool_calls)