from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

TONE = "friendly"
AUDIENCE = "beginners"

template = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Use a {tone} tone. "
            "Your audience is {audience}. Keep answers short."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

def build_messages(history, tone=TONE, audience=AUDIENCE):
    return template.invoke({"messages": history, "tone": tone, "audience": audience}).to_messages()