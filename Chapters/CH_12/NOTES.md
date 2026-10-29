# Ch 12: Tool binding

**What it does:** Three tools (calculator, current date/time, web search) bound to the model with `bind_tools`. The model only REQUESTS calls; my code runs them.
**When I'd use it:** When the model needs exact maths, live data, or access to something outside its training.
**One way it breaks:** If the there is a typo in the custom tools, the program might break or wont work as expected

## First look: `python -m Chapters.CH_12.tools_bot`
The output of response.tool_calls for the prompt "What is 5 times 100? then divide by 20, then add 200." is:
Tool calls: `[{'name': 'calculator', 'args': {'operation': 'multiply', 'a': 5, 'b': 100}, 'id': 'call_nLPkUKkMHNHdnddVyqEl4RGb', 'type': 'tool_call'}`
- The model broke down the problem to solve each equation at a time ujsing the `calculator` tool.
- The model breaks down the user query into smaller parts, so it needs to call the tool as long as the model doesn't get what the user wants.


## Docstring experiment (`python -m Chapters.CH_12.tally_experiment`)
| Prompt | Expected | Clear picked | Vague picked |
|---|---|---|---|
| What is 17 times 23? | calculator | calculator | calculator |
| I have 3 boxes with 48 pearls each. How many  | calculator | calculator | None |
| What is 1250 divided by 25? | calculator | calculator | calculator |
| Subtract 89 from 400. | calculator | calculator | calculator |
| What time is it right now? | get_current_datetime | get_current_datetime | get_current_datetime |
| What is today's date? | get_current_datetime | get_current_datetime | get_current_datetime |
| Which day and time is it at this moment? | get_current_datetime | get_current_datetime | get_current_datetime |
| What is the latest news about the Python prog | contextdev_search_tool | contextdev_search_tool | contextdev_search_tool |
| Who is the current CEO of Nvidia? | contextdev_search_tool | contextdev_search_tool | None |
| What is the price of a Raspberry Pi 5 right n | contextdev_search_tool | contextdev_search_tool | contextdev_search_tool |

Right tool chosen: clear 10/10, vague 8/10

- The clear tools have a descriptive Doc String compared to the vauge tools, That is why the LLm was able to select more clear tools than the vauge tools.

## Gate: the 4-step tool-call flow, in my own words
1. Bind: Binding the tools with the LLM
2. Model requests: The model gets invoked with the custom tool to solve the user query
3. My code runs: Each time the LLM gets the whole convos for it to process
4. ToolMessage returns: `ToolMessage(content='{content_here}', tool_call_id='{tool_call_id}')`