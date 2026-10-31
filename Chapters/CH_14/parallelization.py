from typing import Annotated, List, Literal, Union, TypedDict
from Chapters.CH_6.llm import get_llm
from langchain_core.tools import tool
from operator import add
import time
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END


class graph_schema(TypedDict):
    topic : str
    insta : str
    linkedin : str
    twitter : str



def get_insta_post(state:graph_schema) -> graph_schema:
    '''
    A tool that generates an Instagram post based on a given topic.
    '''
    t1 = time.perf_counter()
    query = state['topic']


    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a professional post caption writer for Instagram. Make sure the caption is engaging.'),
            ('user', 'I want you to make just the Instagram caption for me on this topic: {subject}')
        ]
    )
    llm = get_llm()
    chain = prompt | llm
    response = chain.invoke({'subject':query})

    t2 = time.perf_counter()
    print(f"Instagram post generation time: {t2 - t1:.2f} seconds")

    return {'insta': response.content}


def get_linkedin_post(state:graph_schema) -> graph_schema:
    '''
    A tool that generates a LinkedIn post based on a given topic.
    '''
    t1 = time.perf_counter()
    query = state['topic']

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a professional post caption maker for Linkedin posts. Make sure the caption is professional and engaging.'),
            ('user', 'I want you to make just the LinkedIn caption for me on this topic: {subject}')
        ]
    )
    llm = get_llm()
    chain = prompt | llm
    response = chain.invoke({'subject':query})

    t2 = time.perf_counter()
    print(f"LinkedIn post generation time: {t2 - t1:.2f} seconds")

    return {'linkedin': response.content}


def get_twitter_post(state:graph_schema) -> graph_schema:
    '''
    A tool that generates an X(twitter) post based on a given topic.
    '''
    t1 = time.perf_counter()
    query = state['topic']

    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', 'You are a professional post caption writer for X(twitter) posts. Make sure the caption is within 280 characters and is engaging.'),
            ('user', 'I want you to make just the X(twitter) caption for me on this topic: {subject}')
        ]
    )
    llm = get_llm()
    chain = prompt | llm
    response = chain.invoke({'subject':query})

    t2 = time.perf_counter()
    print(f"X(twitter) post generation time: {t2 - t1:.2f} seconds")

    return {'twitter': response.content}


graph = StateGraph(graph_schema)

graph.add_node('insta', get_insta_post)
graph.add_node('linkedin', get_linkedin_post)
graph.add_node('twitter', get_twitter_post)

graph.add_edge(START, 'insta')
graph.add_edge(START, 'linkedin')
graph.add_edge(START, 'twitter')

graph.add_edge('insta', END)
graph.add_edge('linkedin', END)
graph.add_edge('twitter', END)

post_graph = graph.compile()

if __name__ == "__main__":
    # Saving the graph as a PNG or Mermaid file
    from pathlib import Path

    here = Path(__file__).parent
    drawing = post_graph.get_graph()
    try:
        (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
        print("Saved graph.png")
    except Exception as e:
        (here / "graph.mmd").write_text(drawing.draw_mermaid())
        print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")

    query = "The importance of AI in modern healthcare"
    out = post_graph.invoke({"topic": query})
    print(out)