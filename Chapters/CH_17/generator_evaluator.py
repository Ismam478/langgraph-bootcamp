from operator import add
from typing import Annotated, List, TypedDict, Literal
from Chapters.CH_6.llm import get_llm
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

MAX_ITERATIONS = 3

class GraphSchema(BaseModel):
    query: str = Field(description="The query to be passed to Generator Node.")
    results: Annotated[List[str], add] = Field(description="The results list from the Generator Node.", default_factory=list)
    evaluation: bool = Field(description="The evaluation result from the Evaluator Node.", default=False)
    feedback: Annotated[List[str], add] = Field(description="The feedback from the Evaluator Node.", default_factory=list)
    iterations: Annotated[int, add] = Field(description="The number of iterations the Generator Node has been used.", default=0)

class EvaluatorSchema(BaseModel):
    passed: bool = Field(description="If the last result from the Generator Node passed the evaluation based on the user query.")
    feedback: str = Field(description="Feedback from the evaluator regarding the last result.")

def evaluator_node(state: GraphSchema) -> dict:
    """
    Evaluates the last result from the Generator Node based on the user query.
    """
    last_result = state.results[-1]

    llm = get_llm().with_structured_output(EvaluatorSchema)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are a strict QA Evaluator Node in an iterative execution loop.
                Your sole objective is to determine if a generated result completely and accurately answers the user's query.

                CRITICAL RULES:
                1. **Strict Binary Evaluation:** The result must fully satisfy the user's core intent. If it contains partial answers, hallucinations, or misses requested details, it fails.
                2. **Actionable Feedback Only:** If the result fails, you must state exactly what is missing, incorrect, or irrelevant (e.g., "Failed: The response explains what LangGraph is, but fails to answer the user's specific question about how memory works.").
                3. **No Rewriting:** NEVER generate the corrected answer yourself. Only diagnose the gaps so the upstream Generator node can fix them.
                4. **Success State:** If the query is fully answered, set the status to True and set feedback to "Approved." 
                5. **Consistency:** Maintain a friendly tone and style (three keywords from query) throughout the generated content.
                6. **Character limit** Contains 40-60 words"""),
            
            ("user", """USER QUERY:
                {user_query}

                GENERATED RESULT TO EVALUATE:
                {last_result}""")
        ]
    )
    chain = prompt | llm
    result = chain.invoke({"user_query": state.query, "last_result": last_result})
    evaluation = result.passed
    feedback = result.feedback

    print(f"\nEvaluation: {evaluation}, Feedback: {feedback}  [Iteration number: {state.iterations + 1}]")

    return {"evaluation": evaluation, "feedback": [feedback], "iterations": 1}

def generator_node(state: GraphSchema) -> dict:
    """
    Generates a new result based on the user query.
    """
    query = state.query
    last_result = state.results[-1] if state.results else ""
    feedback = state.feedback[-1] if state.feedback else ""

    if not feedback:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages(
            [
                ('system', 'You are a Generator Node. Your task is to generate a result based on the user query.'),
                ('user', 'User Query: {user_query}\n\nGenerate a result based on the user query.')
            ]
        )
        chain = prompt | llm
        new_result = chain.invoke({"user_query": query}).content
    else:
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", """You are a precision-driven Generator Node in an iterative execution loop.
                    Your objective is to generate or revise content based strictly on the user's instructions.

                    CRITICAL REVISION RULES:
                    1. **Prioritize Feedback:** If Evaluator Feedback is provided, treat it as absolute truth. Fix the exact mathematical or stylistic failures listed (e.g., word count or missing keywords).
                    2. **Do Not Regress:** If parts of the previous draft were successful, keep them intact. Only alter what is necessary to pass the evaluation.
                    3. **No Conversational Filler:** Output ONLY the final drafted text. NEVER include preambles, apologies, or meta-commentary (e.g., "Here is the revised version...", "I apologize for the mistake.")."""),
                
                ("user", """USER QUERY / INSTRUCTIONS:
                    {user_query}

                    PREVIOUS DRAFT (If any):
                    {previous_results}

                    EVALUATOR FEEDBACK (If any):
                    {feedback}

                    Generate the optimized response.""")
            ]
        )

        chain = prompt | llm
        new_result = chain.invoke({"user_query": query, "previous_results": last_result, "feedback": feedback}).content        

    return {"results": [new_result]}

def conditional_func(state: GraphSchema):
    """
    Determines whether the graph should progress to the next node.
    """
    should_progress = state.evaluation
    max_iterations = state.iterations

    if max_iterations < MAX_ITERATIONS and not should_progress:
        return 'generator_node'
    else:
        return 'end'


graph = StateGraph(GraphSchema)
graph.add_node('generator_node', generator_node)
graph.add_node('evaluator_node', evaluator_node)

graph.add_edge(START, 'generator_node')
graph.add_edge('generator_node', 'evaluator_node')
graph.add_conditional_edges('evaluator_node', conditional_func, {'generator_node': 'generator_node', 'end': END})

generator_evaluator = graph.compile()

if __name__ == '__main__':
    #### Saving the graph as a PNG or Mermaid file
    from pathlib import Path

    here = Path(__file__).parent
    drawing = generator_evaluator.get_graph()
    try:
        (here / "graph.png").write_bytes(drawing.draw_mermaid_png())
        print("Saved graph.png")
    except Exception as e:
        (here / "graph.mmd").write_text(drawing.draw_mermaid())
        print(f"PNG failed ({type(e).__name__}); saved graph.mmd instead")