import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Orchestrator: fast + cheap for routing decisions
ORCHESTRATOR_MODEL = "openai/gpt-oss-20b"

# Sub-agents: larger model for quality writing and reasoning
GMAIL_MODEL = "openai/gpt-oss-120b"
RESEARCH_MODEL = "openai/gpt-oss-120b"
LINKEDIN_MODEL = "openai/gpt-oss-120b"
