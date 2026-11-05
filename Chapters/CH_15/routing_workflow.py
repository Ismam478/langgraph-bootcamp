from typing import Literal
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from Chapters.CH_6.llm import get_llm


billing = "Queries related to money, invoices, subscriptions, payments, or refunds"
tech = "Queries related to bugs, errors, system outages, login issues, or how to use a specific software feature"
general = "Anything else that doesn't fit into billing or technical support. This could be questions about company policy, opening hours, business inquiries, or general feedback"


# Conditional Router
ROUTER_PROMPT_V1 = f"You are professional categorizer, these are the categories: Billing: {billing}, Tech: {tech}, General: {general}. I want you to find and give me the category of the user's query."
TIE_BREAK_V2 = (
    "Tie-break rule: if the customer asks how to operate a feature of the product, "
    "choose Tech, even when that feature is about payments or billing."
)
ROUTER_PROMPT_V2 = ROUTER_PROMPT_V1 + " " + TIE_BREAK_V2


# Routing graph
class Route(BaseModel):
    category: Literal['billing', 'tech', 'general']


# Router Workflow Graph Schema
class GraphSchema(BaseModel):
    query: str
    category: str = ''
    reply: str = ''


# Conditional Function
def classify(query:str, prompt: str = ROUTER_PROMPT_V2) -> str:
    """
    Classifies the user's query into one of the predefined categories: billing, tech, or general
    """
    llm = get_llm()
    llm_with_schema = llm.with_structured_output(Route)

    llm_prompt = [('system', prompt),('user', query)]

    category = llm_with_schema.invoke(llm_prompt).category

    return category


# Router Node
def router_node(state: GraphSchema) -> GraphSchema:
    """
    The LLM Node to handle queries that require LLM processing.
    """
    query = state.query
    category = classify(query=query)

    return {'category': category}


# Condition Function
def router_condition(state: GraphSchema) -> str:
    """
    The Router Node to decide which node to return.
    """

    category = state.category
    
    if category == 'billing':
        return "billing_node"
    elif category == 'tech':
        return "tech_node"
    elif category == 'general':
        return "general_node"
    else:
        raise ValueError(f"Unknown category: {category}")


def billing_node(state: GraphSchema) -> dict:
    """
    The Billing Node to handle billing queries.
    """
    query = state.query
    llm = get_llm()
    billing_prompt = "You are a billing specialist. Be polite, firm on policy, and always ask for an invoice number if not provided."
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', billing_prompt), ('user', "{user_query}")
        ]
    )
    chain = prompt | llm
    reply = chain.invoke({'user_query': query}).content

    return {'reply': reply}

def tech_node(state: GraphSchema) -> dict:
    """
    The Tech Node to handle technical queries.
    """
    query = state.query
    llm = get_llm()
    tech_prompt = "You are a technical support engineer. Ask for system specs, error logs, and provide clear step-by-step troubleshooting instructions."
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', tech_prompt), ('user', "{user_query}")
        ]
    )
    
    chain = prompt | llm
    reply = chain.invoke({'user_query': query}).content

    return {'reply': reply}

def general_node(state: GraphSchema) -> dict:
    """
    The General Node to handle general queries.
    """
    query = state.query
    llm = get_llm()
    general_prompt = "You are a customer success representative. Be warm, welcoming, and helpful with general inquiries."
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', general_prompt), ('user', "{user_query}")
        ]
    )
    
    chain = prompt | llm
    reply = chain.invoke({'user_query': query}).content

    return {'reply': reply}


graph = StateGraph(GraphSchema)

graph.add_node('billing_node', billing_node)
graph.add_node('tech_node', tech_node)
graph.add_node('general_node', general_node)
graph.add_node('router_node', router_node)

graph.add_edge(START, 'router_node')
graph.add_conditional_edges('router_node', router_condition, {'billing_node':'billing_node', 'tech_node':'tech_node', 'general_node':'general_node'})
graph.add_edge('billing_node', END)
graph.add_edge('tech_node', END)
graph.add_edge('general_node', END)

route_graph = graph.compile()

if __name__ == '__main__':
    #### Saving the graph as a PNG or Mermaid file
    from pathlib import Path

    here = Path(__file__).parent
    drawing = route_graph.get_graph()
    try:
        (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
        print("Saved graph.png")
    except Exception as e:
        (here / "graph.mmd").write_text(drawing.draw_mermaid())
        print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")

    user_query = input("User: ")
    reply = route_graph.invoke({'query': user_query})['reply']

    print(reply)

    