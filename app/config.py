
# Grab environment variables so we can talk to OpenRouter
import os
from dotenv import load_dotenv

# Load up everything from .env right away
load_dotenv()

# API key for OpenRouter, absolutely need this or nothing works
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Default model to use, fallback to free model if nothing specified
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
)

# Fail fast if someone forgot to add their key to .env
if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing. Check your .env file."
    )
