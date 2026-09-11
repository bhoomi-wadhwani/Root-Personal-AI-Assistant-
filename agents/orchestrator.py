import json
from groq import Groq
from agents import gmail_agent, research_agent, linkedin_agent
from config import GROQ_API_KEY, ORCHESTRATOR_MODEL
from memory import memory_store

client = Groq(api_key=GROQ_API_KEY)

_BASE_SYSTEM = """You are a personal AI assistant with long-term memory. You remember the user across conversations and use that knowledge to personalize every response.

Available tools:
- call_gmail_agent: Anything email — draft, send, search, reply
- call_research_agent: Web searches, current info, news, research questions
- call_linkedin_agent: LinkedIn — search people, view profiles, send connection requests, send messages, read feed
- store_memory: Save an important fact about the user permanently

Routing rules:
- "Draft an email about [topic]" → research first, then gmail
- "Send an email to..." → gmail only
- "What is / Who is / Find info on..." → research only
- "LinkedIn / connect with / message [person] on LinkedIn / my feed" → linkedin only
- When user shares personal info (name, job, preferences, habits, people they know) → call store_memory immediately
- Ambiguous → pick the most likely, execute, explain what you did

After an agent completes, summarize the result clearly in 2-3 sentences.
Be conversational and personal — use the user's name if you know it. Never be robotic."""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "call_gmail_agent",
            "description": "Route task to the Gmail specialist (drafting, sending, searching emails)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Full description of the email task to perform"}
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_research_agent",
            "description": "Route task to the Research specialist (web search, current events, finding information)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "The research question or topic to investigate"}
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "call_linkedin_agent",
            "description": "Route task to the LinkedIn specialist (search people, view profiles, connect, message, read feed)",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Full description of the LinkedIn task to perform"}
                },
                "required": ["task"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Permanently save an important fact about the user — name, job, preferences, relationships, habits, anything worth remembering forever",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {
                        "type": "string",
                        "description": "The fact to remember, as a clear statement. E.g. \"User's name is Bhoomi\", \"User prefers formal email tone\", \"User works as a software engineer\"",
                    }
                },
                "required": ["fact"],
            },
        },
    },
]


def run(user_message: str, history: list[dict], user_id: int) -> str:
    facts = memory_store.format_facts(user_id)
    system = _BASE_SYSTEM + (f"\n\n{facts}" if facts else "")

    messages = [{"role": "system", "content": system}]
    messages += history
    messages.append({"role": "user", "content": user_message})

    while True:
        response = client.chat.completions.create(
            model=ORCHESTRATOR_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024,
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content or "Done."

        messages.append(message)

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == "call_gmail_agent":
                result = gmail_agent.run(args["task"])
            elif name == "call_research_agent":
                result = research_agent.run(args["task"])
            elif name == "call_linkedin_agent":
                result = linkedin_agent.run(args["task"])
            elif name == "store_memory":
                memory_store.add_fact(user_id, args["fact"])
                result = f"Remembered: {args['fact']}"
            else:
                result = f"Unknown tool: {name}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
