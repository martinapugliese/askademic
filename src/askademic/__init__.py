import os
import sys

from rich.console import Console

console = Console()

# Check if running inside a test framework
IS_TEST_ENVIRONMENT = "pytest" in sys.modules

# Check this here because if not set the following imports will fail
if not os.getenv("GEMINI_API_KEY"):
    console.print(
        """
    [bold red]The GEMINI_API_KEY environment variable is not set.[/bold red]
    [bold red]See the README for instructions.[/bold red]
    """
    )
    if not IS_TEST_ENVIRONMENT:
        sys.exit("")
    else:
        raise RuntimeError("GEMINI_API_KEY is not set. Exiting during tests.")

os.makedirs("logs", exist_ok=True)
