import argparse
import asyncio
import os

import boto3
import logfire
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from evals_allower import run_evals as run_evals_allower
from evals_article import run_evals as run_evals_article
from evals_general import run_evals as run_evals_general
from evals_orchestrator import run_evals as run_evals_orchestrator
from evals_question import run_evals as run_evals_question
from evals_summary import run_evals as run_evals_summary
from rich.console import Console

# Load environment and configure logfire early
load_dotenv()
logfire_token = os.getenv("LOGFIRE_TOKEN", None)
if logfire_token:
    logfire.configure(token=logfire_token, console=False)
    logfire.instrument_pydantic_ai()

console = Console()

ALL_MODELS = ["gemini", "claude", "claude-aws-bedrock"]
ALL_EVALS = ["allower", "orchestrator", "summary", "question", "article", "general"]

EVAL_RUNNERS = {
    "allower": run_evals_allower,
    "orchestrator": run_evals_orchestrator,
    "summary": run_evals_summary,
    "question": run_evals_question,
    "article": run_evals_article,
    "general": run_evals_general,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run askademic evaluation suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python evals.py                           # Run all evals with all models
  python evals.py -m gemini                 # Run all evals with gemini only
  python evals.py -e article question       # Run article and question evals
  python evals.py -m claude -e allower      # Run allower eval with claude only

Available models: {', '.join(ALL_MODELS)}
Available evals: {', '.join(ALL_EVALS)}
        """,
    )
    parser.add_argument(
        "-m",
        "--model",
        nargs="+",
        choices=ALL_MODELS,
        default=ALL_MODELS,
        metavar="MODEL",
        help=f"Model(s) to run evals with. Choices: {', '.join(ALL_MODELS)}",
    )
    parser.add_argument(
        "-e",
        "--eval",
        nargs="+",
        choices=ALL_EVALS,
        default=ALL_EVALS,
        metavar="EVAL",
        help=f"Eval(s) to run. Choices: {', '.join(ALL_EVALS)}",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available models and evals, then exit",
    )
    return parser.parse_args()


def check_model_credentials(model_family: str) -> bool:
    """Check if credentials are available for the given model family."""
    if model_family == "gemini" and os.getenv("GOOGLE_API_KEY") is None:
        console.print(
            "[bold red]GOOGLE_API_KEY environment variable is not set. "
            "Skipping gemini evals.[/bold red]"
        )
        return False

    if model_family == "claude" and os.getenv("ANTHROPIC_API_KEY") is None:
        console.print(
            "[bold red]ANTHROPIC_API_KEY environment variable is not set. "
            "Skipping claude evals.[/bold red]"
        )
        return False

    if model_family == "claude-aws-bedrock":
        try:
            _ = boto3.client("sts").get_caller_identity()
        except (ClientError, NoCredentialsError):
            console.print(
                "[bold red]AWS credentials are not set or invalid. "
                "Skipping claude-aws-bedrock evals.[/bold red]"
            )
            return False

    return True


async def main():
    args = parse_args()

    if args.list:
        console.print("[bold]Available models:[/bold]")
        for model in ALL_MODELS:
            console.print(f"  - {model}")
        console.print("\n[bold]Available evals:[/bold]")
        for eval_name in ALL_EVALS:
            console.print(f"  - {eval_name}")
        return

    load_dotenv()

    models = args.model
    evals = args.eval

    console.print(f"[bold cyan]Models:[/bold cyan] {', '.join(models)}")
    console.print(f"[bold cyan]Evals:[/bold cyan] {', '.join(evals)}\n")

    for model_family in models:
        if not check_model_credentials(model_family):
            continue

        console.print(f"\n[bold blue]===== Model: {model_family} =====[/bold blue]")

        for eval_name in evals:
            console.print(
                f"\n[bold magenta]Running {eval_name} evals...[/bold magenta]"
            )
            await EVAL_RUNNERS[eval_name](model_family)


if __name__ == "__main__":
    asyncio.run(main())
