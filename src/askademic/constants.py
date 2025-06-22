# User instructions
INSTRUCTIONS = """
Instructions:
- Type "llm" to choose the LLM family (default is 'gemini')
- Type "reset" to reset the memory
- Type "history" to see the memory history
- Type "exit" or CTRL+D to quit
- Type "help" to see instructions again
"""

# LLM model IDs
GEMINI_2_FLASH_MODEL_ID = "gemini-2.0-flash"
CLAUDE_HAIKU_3_5_MODEL_ID = "anthropic:claude-3-5-haiku-latest"
CLAUDE_HAIKU_3_5_BEDROCK_MODEL_ID = "{region}.anthropic.claude-3-5-haiku-20241022-v1:0"
NOVA_PRO_BEDORCK_MODEL_ID = "{region}.amazon.nova-pro-v1:0"
MISTRAL_LARGE_MODEL_ID = "mistral:mistral-large-latest"

# ARXIV URLS
ARXIV_BASE_URL = "http://export.arxiv.org/api/query?"

# User-agents for requests (to rotate)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]
