# User instructions
INSTRUCTIONS = """
Instructions:
- Type "reset" to reset the memory
- Type "history" to see the memory history
- Type "exit" or CTRL+D to quit
- Type "help" to see instructions again
"""

# LLM model IDs (using provider:model syntax)
GEMINI_2_FLASH_MODEL_ID = "google-gla:gemini-2.0-flash"
CLAUDE_HAIKU_4_5_MODEL_ID = "anthropic:claude-haiku-4-5-latest"
CLAUDE_HAIKU_4_5_BEDROCK_MODEL_ID = (
    "bedrock:{region}.anthropic.claude-haiku-4-5-20251001-v1:0"
)
NOVA_LITE_BEDROCK_MODEL_ID = "bedrock:{region}.amazon.nova-2-lite-v1:0"
MISTRAL_LARGE_MODEL_ID = "mistral:mistral-large-latest"

# ARXIV URLS
ARXIV_BASE_URL = "http://export.arxiv.org/api/query?"

# User-agents for requests (to rotate)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]
