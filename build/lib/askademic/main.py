import asyncio
import logging
import time
from datetime import datetime
from inspect import cleandoc

from pydantic_ai.usage import UsageLimits
from rich.console import Console
from rich.prompt import Prompt

from askademic.agents import allower_agent, orchestrator_agent
from askademic.memory import Memory

console = Console()
logger = logging.getLogger(__name__)


async def _main():

    console.print(
        cleandoc(
            """
    [bold cyan]Hello, welcome to Askademic![/bold cyan] :smiley:
    [bold cyan]
    I can assist you with
    - summarizing the latest literature in a field or topic (published in the latest available day),
    - answering specific questions
    [/bold cyan]
    """
        )
    )

    memory = Memory(max_request_tokens=1e5)

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

                allower = await allower_agent.run(
                    user_question,
                    usage_limits=UsageLimits(request_limit=20),  # limit to 10 requests
                )

                if allower.data.is_scientific:
                    agent_result = await orchestrator_agent.run(
                        user_question,
                        usage_limits=UsageLimits(request_limit=20),  # limit requests
                        message_history=memory.get_messages(),
                    )
                    for k in agent_result.data.__dict__:
                        console.print(f"{k}: {getattr(agent_result.data, k)}")

                    memory.add_message(
                        agent_result.usage().total_tokens,
                        agent_result.new_messages(),
                    )
                else:
                    console.print(
                        "[bold red]This question isn't scientific—it's more of a disturbance in the Force! Try again, young Padawan.[/bold red]"
                    )

                break
            except Exception as e:
                logger.error(
                    f"{datetime.now()}: An error has occurred: {e}, retrying in 60 seconds..."
                )
                time.sleep(60)
                attempts += 1


if __name__ == "__main__":
    # TODO: this fix is temporary. We should monitor pydantic-ai issues and see when they solve it
    # The workaround is described here: https://github.com/pydantic/pydantic-ai/issues/748
    asyncio.run(_main())
