from pydantic import BaseModel, Field
from operator import add
from Chapters.CH_6.llm import get_llm
from langgraph.graph import StateGraph, START, END
from typing import Annotated, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver

class GraphSchema(BaseModel):
    messages: Annotated[list, add_messages]
    summary: str = Field(default='', description="A summary of the conversation so far.")


def chatbot(state: GraphSchema) -> dict:

    messages = []
    query = state.messages
    summary = state.summary

    if summary:
        messages.append(SystemMessage(content=f"Existing Summary: {summary}, Use this summary to answer the user query. Dont add things on your own."))

    messages.extend(query)


    llm = get_llm()
    result = llm.invoke(messages)

    return {'messages': [result]}

def summarization(state: GraphSchema) -> dict:

    existing_summary = state.summary
    query = state.messages

    if existing_summary:
        prompt = (
            f"Existing Summary: {existing_summary}, Extend the summary using only the important things from Conversation, keep it concise and short. Dont add same thing twice, and dont add things that are not in the conversation."
        )
    else:
        prompt = (
            "Summarize only and only the important things from the conversation, keep it concise and short. Dont add same thing twice, and never ever add things that are not in the conversation."
        )

    messages_for_summary = query + [HumanMessage(content=prompt)]

    llm = get_llm()
    response = llm.invoke(messages_for_summary)

    messages_to_remove = query[:-2]

    return {'summary': response.content, 'messages': [RemoveMessage(id=m.id) for m in messages_to_remove]}

def summary_condition(state: GraphSchema):
    if len(state.messages) >= 6:
        return 'summarization'
    else:
        return 'end'

def show_state(graph, config):
    snap = graph.get_state(config)
    vals = snap.values
    print(f"\n----STATE SNAPSHOT----")
    print("Summary: ", vals.get('summary', ''))
    print("num_messages: ", len(vals.get('messages', [])))
    print("messages:")
    for m in vals.get('messages', []):
        print("-", type(m).__name__, ":", m.content[:80])

graph = StateGraph(GraphSchema)
graph.add_node('chatbot', chatbot)
graph.add_node('summarization', summarization)

graph.add_edge(START, 'chatbot')
graph.add_conditional_edges('chatbot', summary_condition, {'summarization': 'summarization', 'end': END})
graph.add_edge('summarization', END)

config = {'configurable': {'thread_id': 'a'}}

if __name__ == '__main__':
    with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
        checkpointer.setup()

        chatbot_graph = graph.compile(checkpointer=checkpointer)

    #### Saving the graph as a PNG or Mermaid file
        from pathlib import Path

        here = Path(__file__).parent
        drawing = chatbot_graph.get_graph()
        try:
            (here / "chatbot_graph.png").write_bytes(drawing.draw_mermaid_png())
            print("Saved graph.png")
        except Exception as e:
            (here / "chatbot_graph.mmd").write_text(drawing.draw_mermaid())
            print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")

    #### Running the chatbot
        while True:
            user_input = input("User: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting....")
                break

            response = chatbot_graph.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)

            print(f"Chatbot: {response['messages'][-1].content}")
            show_state(chatbot_graph, config)