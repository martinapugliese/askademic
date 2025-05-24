import asyncio
import logging
import time
from datetime import datetime
from inspect import cleandoc
from io import StringIO

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from pydantic_ai.usage import UsageLimits
from rich.console import Console
from rich.prompt import Prompt

from askademic.allower import allower_agent_base
from askademic.memory import Memory
from askademic.orchestrator import orchestrator_agent_base
from askademic.prompts.general import USER_PROMPT_ALLOWER_TEMPLATE
from askademic.utils import choose_model

console = Console()
session = PromptSession(history=FileHistory(".cli_history"))

today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


async def get_llm() -> str:
    return Prompt.ask(
        """[bold yellow]Choose your LLM family: type 'gemini' for Gemini (preferred)
    and 'claude' for Claude (experimental)[/bold yellow]"""
    )


async def ask_user_question():
    markup_prompt = (
        "[bold yellow]Ask a question (type 'help' for instructions):[/bold yellow] 💬 "
    )

    # This is to make sure the cursor moves correctly when typing in the terminal
    with StringIO() as buf:
        rich_console = Console(file=buf, force_terminal=True, color_system="truecolor")
        rich_console.print(markup_prompt, end="")
        ansi_prompt = buf.getvalue()
    return await session.prompt_async(ANSI(ansi_prompt))


async def ask_me():

    console.print(
        cleandoc(
            """
    [bold cyan]Hello, welcome to Askademic![/bold cyan] :smiley:
    [bold cyan]
    I work off of data from arXiv. You can ask me to:
    - summarize the latest literature (published in the latest available day)
    in an arXiv category or subcategory,
    - find answers for specific research questions/topics
    - retrieve a specific paper by title or arXiv URL

    Ask me a question with either of these requests.
    I will do the heavy lifting for you, you can ask follow-up questions too.
    There will be logs in a "logs" folder, they're filenamed with the date of the day.

    Instructions:
    - Type "reset" to reset the memory
    - Type "history" to see the memory history
    - Type "exit" or CTRL+D to quit
    - Type "help" to see this message again

    [/bold cyan]
    """
        )
    )

    memory = Memory(max_request_tokens=1e5)

    # ask user to choose the model family
    user_model = await get_llm()

    while True:

        try:

            user_question = await ask_user_question()

            if user_question.lower() == "exit":
                console.print("[bold cyan]Goodbye![/bold cyan] :wave:")
                break

            if user_question == "reset":
                console.print("[bold cyan]Resetting memory...[/bold cyan]")
                memory.clear_history()
                continue

            if user_question == "history":
                console.print("[bold cyan]Memory history:[/bold cyan]")
                for m in memory.get_messages():
                    console.print(m)
                continue

            if user_question == "help":
                console.print(
                    cleandoc(
                        """
                [bold cyan]Instructions:
                - Type "reset" to reset the memory
                - Type "history" to see the memory history
                - Type "exit" or CTRL+D to quit
                - Type "help" to see this message again[/bold cyan]
                """
                    )
                )
                continue
        except EOFError:
            console.print("[bold cyan]Goodbye![/bold cyan] :wave:")
            break

        attempts, max_attempts = 0, 10
        console.print("[bold cyan]Working for you ...[/bold cyan]")
        while attempts < max_attempts:
            try:

                allower_agent = allower_agent_base
                allower_agent.model = choose_model(user_model)
                allower_result = await allower_agent.run(
                    USER_PROMPT_ALLOWER_TEMPLATE.format(question=user_question),
                    usage_limits=UsageLimits(request_limit=20),  # limit to 20 requests
                    message_history=memory.get_messages()[
                        -2:
                    ],  # only the last 2 messages to keep the context, with 1 it may lose it
                )
                logger.info(f"{datetime.now()}: Allower run")

                if allower_result.output.is_scientific:
                    orchestrator_agent = orchestrator_agent_base
                    orchestrator_agent.model = choose_model(user_model)
                    orchestrator_result = await orchestrator_agent.run(
                        user_question,
                        usage_limits=UsageLimits(request_limit=20),  # limit requests
                        message_history=memory.get_messages(),
                    )
                    for k in orchestrator_result.output.__dict__:
                        console.print(f"{k}: {getattr(orchestrator_result.output, k)}")

                    memory.add_message(
                        orchestrator_result.usage().total_tokens,
                        orchestrator_result.new_messages(),
                    )
                else:
                    pun = allower_result.output.pun
                    console.print(
                        f"""{pun} - Ask me something scientific please! :smiley:
                    """
                    )

                break
            except Exception as e:
                logger.error(f"An error has occurred: {e}, retrying in 60 seconds...")
                time.sleep(60)
                attempts += 1


# TODO: we have to wrap because main can't be async
# this fix is temporary. We should monitor pydantic-ai issues and see when they solve it
# The workaround is described here: https://github.com/pydantic/pydantic-ai/issues/748
def main():

    asyncio.run(ask_me())


if __name__ == "__main__":
    main()
