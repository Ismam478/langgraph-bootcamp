# Ch 5: OpenAI API

**What it does:** Sends a system + user message, prints the answer and token usage, and estimates the cost.
**When I'd use it:** Before running anything at scale, to know what a run will cost.

## Prices used 
- Model: `gpt-5-nano`  Input: $0.05 per 1M tokens  Output: $0.4 per 1M tokens  Source + date: 2025-08-07

## Gate answers 
- What is a token?
- Tokens are human words/ sentences splitted in smaller chunks and converted into numbers, so that LLM can read the input easily
- Why do output tokens cost more than input tokens?
- GPUs can process input tokens in parallel, but to generate each token, AI needs to complete the previous one and run the work sequentially. 
