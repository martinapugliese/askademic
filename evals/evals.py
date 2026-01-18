import asyncio
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from evals_allower import run_evals as run_evals_allower
from evals_article import run_evals as run_evals_article
from evals_general import run_evals as run_evals_general
from evals_orchestrator import run_evals as run_evals_orchestrator
from evals_question import run_evals as run_evals_question
from evals_summary import run_evals as run_evals_summary
from rich.console import Console

console = Console()


async def main():

    load_dotenv()

    for model_family in [
        "gemini",
        "claude",
        "claude-aws-bedrock",
        "nova-pro-aws-bedrock",
    ]:

        if model_family == "gemini" and os.getenv("GOOGLE_API_KEY") is None:
            console.print(
                """
                [bold red]GOOGLE_API_KEY environment variable is not set.
                Skipping evals.[/bold red]
                """
            )
            continue

        if model_family == "claude" and os.getenv("ANTHROPIC_API_KEY") is None:
            console.print(
                """
                [bold red]ANTHROPIC_API_KEY environment variable is not set.
                Skipping CLAUDE evals.[/bold red]
                """
            )
            continue

        if model_family in ("claude-aws-bedrock", "nova-pro-aws-bedrock"):
            try:
                _ = boto3.client("sts").get_caller_identity()
            except (ClientError, NoCredentialsError):
                console.print(
                    f"""[bold red]AWS credentials are not set or invalid.
                    Skipping {model_family} evals.[/bold red]"""
                )
                continue

        console.print("\n[bold magenta]Running allower evals...[/bold magenta]")
        await run_evals_allower(model_family)

        console.print("\n[bold magenta]Running orchestrator evals...[/bold magenta]")
        await run_evals_orchestrator(model_family)

        console.print("\n[bold magenta]Running summary evals...[/bold magenta]")
        await run_evals_summary(model_family)

        console.print("\n[bold magenta]Running question evals...[/bold magenta]")
        await run_evals_question(model_family)

        console.print("\n[bold magenta]Running article evals...[/bold magenta]")
        await run_evals_article(model_family)

        console.print("\n[bold magenta]Running general agent evals...[/bold magenta]")
        await run_evals_general(model_family)


if __name__ == "__main__":
    asyncio.run(main())
