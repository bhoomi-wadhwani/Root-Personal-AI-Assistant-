import json
from groq import Groq
from tools.search_tools import web_search
from config import GROQ_API_KEY, RESEARCH_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a research specialist. Your job is to search the web,
gather current information, and deliver clear, well-structured summaries.

Always use the web_search tool before answering — never rely on training data alone
for facts that could have changed. Cite sources when relevant."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information on any topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5)",
                    },
                },
                "required": ["query"],
            },
        },
    }
]


def run(task: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    while True:
        response = client.chat.completions.create(
            model=RESEARCH_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=2048,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "Research complete."

        messages.append(message)

        for tool_call in message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            results = web_search(args["query"], args.get("max_results", 5))
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(results),
            })
