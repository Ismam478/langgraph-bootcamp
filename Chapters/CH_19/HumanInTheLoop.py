from pydantic import BaseModel, Field
from Chapters.CH_6.llm import get_llm
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.sqlite import SqliteSaver
import sys

MIN_WORDS = 50
MAX_WORDS = 125

class GraphSchema(BaseModel):
    topic: str = Field(description="The topic to write email.")
    results: str = Field(description="The generated response from LLM", default='')
    feedback : str = Field(description="Feedback for evaluation for the email if user doesn't approve", default='')


def draft_node(state: GraphSchema) -> dict:

    topic = state.topic
    results = state.results
    feedback = state.feedback

    if feedback:
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', f"You are an email writer and reviewer. Write a professional email between {MIN_WORDS} to {MAX_WORDS} words and make sure to follow user's feedback."),
                ('user', """I want you to evaluate my email according to my feedback :{feedback}
                Previous email draft: {results}""")
            ]
        )
        llm = get_llm()
        chain = prompt | llm
        response = chain.invoke({'feedback': feedback, 'results': results})
    else:
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', f"You are an email writer and reviewer. Write a professional email between {MIN_WORDS} to {MAX_WORDS} words."),
                ('user', """I want you to write an email about the following topic: {topic}""")
            ]
        )
        llm = get_llm()
        chain = prompt | llm
        response = chain.invoke({'topic': topic})

    return {'results': response.content, 'feedback': ''}


def approval_node(state: GraphSchema) -> Command[Literal['write', 'draft']]:
    
    decision = interrupt({"draft": state.results})

    action = decision["action"]

    if action == "approve":
        return Command(goto="write")
    elif action == "edit":
        return Command(goto="write", update={"results": decision["text"]})
    elif action == "reject":
        return Command(goto="draft", update={"feedback": decision["feedback"]})
    else:
        raise ValueError(f"Unknown Action: {action}")


def write_email_to_txt(state: GraphSchema) -> dict:
    from pathlib import Path
    here = Path(__file__).parent
    with open((here / "email_draft.txt"), "a") as f:
        f.write(f"{state.results}\n{'-'*40}\n")

    print("\nEmail Saved Successfully")
    return {}


def ask_human(draft:str):

    print("\n----- DRAFT -----\n" + draft + "\n-----------------")
    decision = input("approve / reject / edit:").lower().strip()

    if decision == 'approve':
        return {'action': 'approve'}
    elif decision == 'reject':
        return {'action': 'reject', 'feedback': input("Enter Your Feedback: ")}
    elif decision == 'edit':
        return {"action": "edit", "text": input("Enter Your Edited Draft: ")}
    else:
        print("Please type approve, reject or edit.")
    return ask_human(draft)

def review_loop(draft:str, app, config):
    while True:
        decision = ask_human(draft)
        result = app.invoke(Command(resume=decision), config)
        if not '__interrupt__' in result:
            break
        draft = result['__interrupt__'][0].value['draft']
    print(f"Email Approved and Sent Successfully!")

builder = StateGraph(GraphSchema)
builder.add_node('draft', draft_node)
builder.add_node('approval', approval_node)
builder.add_node('write', write_email_to_txt)

builder.add_edge(START, 'draft')
builder.add_edge('draft', 'approval')
builder.add_edge('write', END)


config = {'configurable': {'thread_id': 'a'}}

if __name__ == '__main__':
    from pathlib import Path
    here = Path(__file__).parent

    mode = sys.argv[1] if len(sys.argv) > 1 else 'run'

    with SqliteSaver.from_conn_string((here/ "checkpoints.sqlite")) as checkpointer:
        checkpointer.setup()

        app = builder.compile(checkpointer=checkpointer)

        #### Saving the graph as a PNG or Mermaid file
        drawing = app.get_graph()
        try:
            (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
            print("Saved graph.png")
        except Exception as e:
            (here / "graph.mmd").write_text(drawing.draw_mermaid())
            print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")

        if mode == 'start':
            topic = input("Enter a topic to draft an email: ").strip()
            response = app.invoke({'topic': topic}, config=config)
            print("<<<<<Paused for next Invocation>>>>>")

        elif mode == 'resume':
            state = app.get_state(config=config)
            if not state.next:
                print("Nothing is waiting for approval")
            else:
                print(f"Resuming the Work {'-'*40}")
                draft = state.tasks[0].interrupts[0].value['draft']
                review_loop(draft, app, config)

        else:
            ### Running the chatbot
            while True:
                user_input = input("Enter a topic to draft an email: ").strip()
                
                if user_input.lower() in ("exit", "quit"):
                    print("Exiting....")
                    break

                response = app.invoke({'topic': user_input}, config=config)
                draft = response['__interrupt__'][0].value['draft']
                review_loop(draft, app, config)
            