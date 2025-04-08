"""Configuration settings for the Meta Prompt Generator."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "anthropic/claude-3-haiku@20240307"  

# Backup models in case the primary one fails
BACKUP_MODELS = [
    "anthropic/claude-3-haiku@20240307",
    "anthropic/claude-3-sonnet@20240229",
    "openai/gpt-3.5-turbo",
    "google/gemini-pro"
]

# System Messages
META_SYSTEM_MESSAGE = """You are an expert prompt engineer specializing in data extraction from documents. 
Your task is to create a precise and effective prompt that will enable an LLM to extract structured data from various document types.
The prompt you generate should:
1. Be clear and unambiguous
2. Be detailed yet concise
3. Include specific instructions for formatting the output (typically JSON)
4. Handle edge cases and ambiguities
5. Guide the model to extract only the information that's requested

Your prompts should follow a consistent structure:
- A clear statement of purpose
- Context for the extraction task
- Specific data fields to extract
- Format instructions with examples
- Guidelines for handling missing or uncertain data
"""

# Template Settings
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
