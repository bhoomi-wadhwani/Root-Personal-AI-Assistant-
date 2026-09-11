import json
from groq import Groq
from tools.gmail_tools import draft_email, send_email, search_emails
from config import GROQ_API_KEY, GMAIL_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a Gmail specialist. You help users manage their email inbox:
- Draft professional, well-structured emails when asked
- Send emails only when the user explicitly says to send (not just draft)
- Search and summarize email threads clearly

Write emails that are professional but natural — not stiff or corporate. Match the
tone the user describes. Always show a preview of what you drafted or sent."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "draft_email",
            "description": "Create and save a draft email to Gmail (does NOT send it)",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Full email body text"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email immediately — use only when user explicitly says to send",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Recipient email address"},
                    "subject": {"type": "string", "description": "Email subject line"},
                    "body": {"type": "string", "description": "Full email body text"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_emails",
            "description": "Search Gmail inbox. Supports Gmail search syntax (from:, subject:, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Gmail search query e.g. 'from:boss@co.com' or 'subject:invoice'",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max emails to return (default 5)",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

_TOOL_MAP = {
    "draft_email": lambda inp: draft_email(inp["to"], inp["subject"], inp["body"]),
    "send_email": lambda inp: send_email(inp["to"], inp["subject"], inp["body"]),
    "search_emails": lambda inp: search_emails(inp["query"], inp.get("max_results", 5)),
}


def run(task: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    while True:
        response = client.chat.completions.create(
            model=GMAIL_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=2048,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "Email task complete."

        messages.append(message)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            if name in _TOOL_MAP:
                result = _TOOL_MAP[name](args)
            else:
                result = {"error": f"Unknown tool: {name}"}

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })
