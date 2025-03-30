import asyncio
import logging
import time
from inspect import cleandoc

import nest_asyncio
from pydantic_ai.usage import UsageLimits
from rich.console import Console
from rich.prompt import Prompt

from agents import orchestrator_agent

nest_asyncio.apply()  # Allows nesting of event loops

console = Console()
logger = logging.getLogger(__name__)


async def main():

    console.print(
        cleandoc(
            """
    [bold cyan]Hello, welcome to the arXivMuse![/bold cyan] :smiley:
    [bold cyan]
    I can assist you with
    - summarizing the latest literature in a field or topic (published in the latest available day),
    - answering specific questions
    [/bold cyan]
    """
        )
    )

    while True:
        user_question = Prompt.ask(
            "[bold yellow]Ask me a question (or type 'exit' to quit)[/bold yellow] :speech_balloon:"
        )

        if user_question.lower() == "exit":
            console.print("[bold cyan]Goodbye![/bold cyan] :wave:")
            break

        attempts = 0
        max_attempts = 10

        console.print(f"[bold cyan]Working for you ...[/bold cyan]")

        while attempts < max_attempts:

            try:
                agent_result = await orchestrator_agent.run(
                    user_question,
                    usage_limits=UsageLimits(request_limit=20),  # limit requests
                )
                for k in agent_result.data.__dict__:
                    console.print(f"{k}: {getattr(agent_result.data, k)}")

                break
            except Exception as e:
                logger.error(f"An error has occurred: {e}, retrying in 60 seconds...")
                time.sleep(60)
                attempts += 1


if __name__ == "__main__":
    asyncio.run(main())
