import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
GROK_API_KEY = os.getenv('GROK_API_KEY')

ANTHROPIC_URL = "https://api.anthropic.com/v1/"
GROK_URL = "https://api.x.ai/v1"
OLLAMA_URL = "http://localhost:11434/v1"

openai = OpenAI()
anthropic = OpenAI(api_key=ANTHROPIC_API_KEY, base_url=ANTHROPIC_URL)
grok = OpenAI(api_key=GROK_API_KEY, base_url=GROK_URL)
ollama = OpenAI(api_key="ollama", base_url=OLLAMA_URL)

MODELS = ["gpt-5", "claude-sonnet-4-5", "grok-4", "gpt-oss:120b:cloud", "minimax-m2:cloud", "deepseek-v3.2:cloud", "kimi-k2-thinking:cloud"]

CLIENTS = {
    "gpt-5": openai,
    "claude-sonnet-4-5": anthropic,
    "grok-4": grok, 
    "gpt-oss:120b:cloud": ollama, 
    "minimax-m2:cloud": ollama, 
    "deepseek-v3.2:cloud": ollama, 
    "kimi-k2-thinking:cloud": ollama
}

def get_client(model_name: str):
    """Get the API client for a specific model"""
    return CLIENTS.get(model_name)