from langchain_core.messages import SystemMessage, HumanMessage

from Chapters.CH_6.llm import get_llm
from Chapters.CH_12.tools_bot import clear_tools, vauge_tools, system_prompt

CASES = [
    ("What is 17 times 23?", "calculator"),
    ("I have 3 boxes with 48 pearls each. How many pearls in total?", "calculator"),
    ("What is 1250 divided by 25?", "calculator"),
    ("Subtract 89 from 400.", "calculator"),
    ("What time is it right now?", "get_current_datetime"),
    ("What is today's date?", "get_current_datetime"),
    ("Which day and time is it at this moment?", "get_current_datetime"),
    ("What is the latest news about the Python programming language?", "contextdev_search_tool"),
    ("Who is the current CEO of Nvidia?", "contextdev_search_tool"),
    ("What is the price of a Raspberry Pi 5 right now?", "contextdev_search_tool"),
]


def first_tool_name(llm_with_tools, prompt):
    response = llm_with_tools.invoke([('system', system_prompt[0].content), ('user', prompt)])
    return response.tool_calls[0]["name"] if response.tool_calls else None


if __name__ == "__main__":
    llm = get_llm()
    sets = {"clear": llm.bind_tools(clear_tools), "vague": llm.bind_tools(vauge_tools)}
    score = {"clear": 0, "vague": 0}

    print("| Prompt | Expected | Clear picked | Vague picked |")
    print("|---|---|---|---|")
    for prompt, expected in CASES:
        picks = {name:first_tool_name(m, prompt) for name, m in sets.items()}
        for name, picked in picks.items():
            score[name] += picked == expected
        print(f"| {prompt[:45]} | {expected} | {picks['clear']} | {picks['vague']} |")

    print(f"\nRight tool chosen: clear {score['clear']}/{len(CASES)}, vague {score['vague']}/{len(CASES)}")
