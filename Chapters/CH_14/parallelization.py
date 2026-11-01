import statistics
from typing import Annotated, List, TypedDict
from Chapters.CH_6.llm import get_llm
from operator import add
import time
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END


class graph_schema(TypedDict):
    topic : str
    insta : str
    linkedin : str
    twitter : str
    research_results : Annotated[List[str], add]
    # research_results : List[str]
    final_results : str



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

    return {'insta': response.content, 'research_results': [response.content]}


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

    return {'linkedin': response.content, 'research_results': [response.content]}


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

    return {'twitter': response.content, 'research_results': [response.content]}

def aggregator(state:graph_schema) -> graph_schema:
    '''
    A tool that aggregates the results from the previous tools.
    '''
    t1 = time.perf_counter()
    results = state['research_results']
    aggregated_results = "\n".join(results)
    t2 = time.perf_counter()
    print(f"Aggregation time: {t2 - t1:.2f} seconds")
    return {'final_results': aggregated_results}

# Parallel Graph Construction
parallel_graph = StateGraph(graph_schema)

parallel_graph.add_node('insta', get_insta_post)
parallel_graph.add_node('linkedin', get_linkedin_post)
parallel_graph.add_node('twitter', get_twitter_post)
parallel_graph.add_node('aggregator', aggregator)

parallel_graph.add_edge(START, 'insta')
parallel_graph.add_edge(START, 'linkedin')
parallel_graph.add_edge(START, 'twitter')

parallel_graph.add_edge(['insta', 'linkedin', 'twitter'], 'aggregator')
parallel_graph.add_edge('aggregator', END)

# parallel_graph.add_edge('insta', END)
# parallel_graph.add_edge('linkedin', END)
# parallel_graph.add_edge('twitter', END)

parallel_post_graph = parallel_graph.compile()


# Sequential Graph Construction
sequential_graph = StateGraph(graph_schema)

sequential_graph.add_node('insta', get_insta_post)
sequential_graph.add_node('linkedin', get_linkedin_post)
sequential_graph.add_node('twitter', get_twitter_post)

sequential_graph.add_edge(START, 'insta')
sequential_graph.add_edge('insta', 'linkedin')
sequential_graph.add_edge('linkedin', 'twitter')
sequential_graph.add_edge('twitter', END)

sequential_post_graph = sequential_graph.compile()


if __name__ == "__main__":
    ##### Saving the graph as a PNG or Mermaid file
    # from pathlib import Path

    # here = Path(__file__).parent
    # drawing = parallel_post_graph.get_graph()
    # drawing_2 = sequential_post_graph.get_graph()
    # try:
    #     (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
    #     (here / "graph_sequential.png").write_bytes(drawing_2.draw_mermaid_png())
    #     print("Saved graph.png and graph_sequential.png")
    # except Exception as e:
    #     (here / "graph.mmd").write_text(drawing.draw_mermaid())
    #     (here / "graph_sequential.mmd").write_text(drawing_2.draw_mermaid())
    #     print(f"PNG failed ({type(e).__name__}); saved graph.mmd and graph_sequential.mmd instead")

    query = "The importance of AI in modern healthcare"

    p_times = []
    s_times = []


    for i in range(3):
        # Parallel execution
        time_start_1 = time.perf_counter()
        
        out_1 = parallel_post_graph.invoke({"topic": query})
        
        time_end_1 = time.perf_counter()
        p_times.append(time_end_1 - time_start_1)
        print(f"\nParallel execution time: {time_end_1 - time_start_1:.2f} seconds\n\n\n")
        # print(out_1)

        # Sequential execution
        time_start_2 = time.perf_counter()
        
        out_2 = sequential_post_graph.invoke({"topic": query})
        
        time_end_2 = time.perf_counter()
        s_times.append(time_end_2 - time_start_2)
        print(f"\n\n\nSequential execution time: {time_end_2 - time_start_2:.2f} seconds")
        # print(out_2)
    print(f"\n\n\n")
    print(f"Parallel Median: {statistics.median(p_times):.2f}s")
    print(f"Sequential Median: {statistics.median(s_times):.2f}s")