import json
from groq import Groq
from tools.linkedin_tools import search_people, get_profile, add_connection, send_message, get_my_feed
from config import GROQ_API_KEY, LINKEDIN_MODEL

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a LinkedIn specialist assistant. You help the user manage their LinkedIn presence:
- Search for people by name, company, or keywords
- Look up detailed profiles
- Send connection requests with a personalized note
- Send direct messages to connections
- Summarize what's happening in their LinkedIn feed

Always be professional but human. When sending connection requests or messages, write them naturally — not like a template.
Summarize search/profile results clearly and highlight what's most useful."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_people",
            "description": "Search LinkedIn for people by name, job title, company, or keywords",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {"type": "string", "description": "Search keywords (name, title, company, etc.)"},
                    "limit": {"type": "integer", "description": "Max results to return (default 5)"},
                },
                "required": ["keywords"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_profile",
            "description": "Get detailed LinkedIn profile info for a person using their public profile ID (the part after linkedin.com/in/)",
            "parameters": {
                "type": "object",
                "properties": {
                    "public_id": {"type": "string", "description": "LinkedIn public profile ID, e.g. 'john-doe-123'"},
                },
                "required": ["public_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_connection",
            "description": "Send a connection request to someone on LinkedIn",
            "parameters": {
                "type": "object",
                "properties": {
                    "public_id": {"type": "string", "description": "LinkedIn public profile ID of the person"},
                    "message": {"type": "string", "description": "Optional personalized note to include with the request (max 300 chars)"},
                },
                "required": ["public_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_message",
            "description": "Send a direct message to a LinkedIn connection",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_public_id": {"type": "string", "description": "LinkedIn public profile ID of the recipient"},
                    "message_text": {"type": "string", "description": "The message to send"},
                },
                "required": ["recipient_public_id", "message_text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_feed",
            "description": "Fetch recent posts from the user's LinkedIn feed",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of posts to fetch (default 5)"},
                },
            },
        },
    },
]

_TOOL_MAP = {
    "search_people": lambda a: search_people(a["keywords"], a.get("limit", 5)),
    "get_profile": lambda a: get_profile(a["public_id"]),
    "add_connection": lambda a: add_connection(a["public_id"], a.get("message", "")),
    "send_message": lambda a: send_message(a["recipient_public_id"], a["message_text"]),
    "get_my_feed": lambda a: get_my_feed(a.get("limit", 5)),
}


def run(task: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    while True:
        response = client.chat.completions.create(
            model=LINKEDIN_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=2048,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "LinkedIn task complete."

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
