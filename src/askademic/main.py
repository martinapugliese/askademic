import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from inspect import cleandoc
from io import StringIO

import boto3
import logfire
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from pydantic_ai.usage import UsageLimits
from rich.console import Console

from askademic.allower import allower_agent_base
from askademic.constants import INSTRUCTIONS
from askademic.memory import Memory
from askademic.orchestrator import orchestrator_agent_base
from askademic.prompts.general import USER_PROMPT_ALLOWER_TEMPLATE
from askademic.utils import choose_model

console = Console()
session = PromptSession(history=FileHistory(".cli_history"))

today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


async def ask_user_question():
    markup_prompt = (
        "[bold yellow]Ask a question (type 'help' for instructions):[/bold yellow] 💬 "
    )

    # This is to make sure the terminal cursor moves correctly
    with StringIO() as buf:
        rich_console = Console(file=buf, force_terminal=True, color_system="truecolor")
        rich_console.print(markup_prompt, end="")
        ansi_prompt = buf.getvalue()
    return await session.prompt_async(ANSI(ansi_prompt))


async def check_environment_variables(user_model: str):

    if user_model == "gemini":
        if not os.getenv("GEMINI_API_KEY"):
            console.print(
                "[bold red]The GEMINI_API_KEY environment variable is not set.[/bold red]"
            )
            sys.exit()
    elif user_model in "claude":
        if not os.getenv("ANTHROPIC_API_KEY"):
            console.print(
                "[bold red]The ANTHROPIC_API_KEY environment variable is not set.[/bold red]"
            )
            sys.exit()
    elif user_model in ("claude-aws-bedrock", "nova-pro-aws-bedrock"):
        try:
            _ = boto3.client("sts").get_caller_identity()
        except boto3.exceptions.ClientError:
            console.print(
                "[bold red]The AWS credentials are not set or invalid.[/bold red]"
            )
            console.print(
                "[bold red]Please set the AWS_ACCESS_KEY_ID "
                + "and AWS_SECRET_ACCESS_KEY environment variables.[/bold red]"
            )
            sys.exit()
    else:
        console.print(
            "[bold red]Invalid model family selected. "
            + "Please choose 'gemini', 'claude', 'claude-aws-bedrock'"
            + " or 'nova-pro-aws-bedrock'.[/bold red]"
        )
        sys.exit()


async def ask_me():

    # load environment variables from .env file
    if not os.path.exists(".env"):
        console.print(
            """
        [bold red]No .env file found.
        Please create one with the required environment variables.[/bold red]"""
        )
        sys.exit()

    load_dotenv()

    logfire_token = os.getenv("LOGFIRE_TOKEN", None)
    user_model = os.getenv("LLM_FAMILY", "gemini")

    console.print(
        cleandoc(
            f"""
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

    {INSTRUCTIONS}

    [/bold cyan]
    """
        )
    )

    memory = Memory(max_request_tokens=1e5)

    # ask user to choose the model family (gemini by default)
    while user_model not in (
        "gemini",
        "claude",
        "claude-aws-bedrock",
        "nova-pro-aws-bedrock",
    ):
        console.print(
            """[bold red]Please configure the LLM family
        to be either "gemini" or "claude", "claude-aws-bedrock"
         or "nova-pro-aws-bedrock"):[/bold red]"""
        )
        return

    await check_environment_variables(user_model)

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
                        f"""
                [bold cyan]
                {INSTRUCTIONS}
                [/bold cyan]
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

                # instrument the calls, do not send to stdout, just to logfire project
                if logfire_token:
                    logfire.configure(token=logfire_token, console=False)
                    logfire.instrument_pydantic_ai()

                allower_agent = allower_agent_base
                model, model_settings = choose_model(user_model)
                allower_agent.model = model
                allower_agent.model_settings = model_settings
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
                    model, model_settings = choose_model(user_model)
                    orchestrator_agent.model = model
                    orchestrator_agent.model_settings = model_settings
                    orchestrator_result = await orchestrator_agent.run(
                        user_question,
                        usage_limits=UsageLimits(request_limit=20),  # limit requests
                        message_history=memory.get_messages(),
                    )
                    for k in orchestrator_result.output.response.__dict__:
                        console.print(
                            f"{k}: {getattr(orchestrator_result.output.response, k)}"
                        )

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
