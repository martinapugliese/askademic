import asyncio

from evals_allower import run_evals as run_evals_allower
from evals_article import run_evals as run_evals_article
from evals_orchestrator import run_evals as run_evals_orchestrator
from evals_question import run_evals as run_evals_question
from evals_summary import run_evals as run_evals_summary
from rich.console import Console

console = Console()


async def main():
    console.print("[bold cyan]:hourglass: Running all evals...[/bold cyan]")
    console.print("\n[bold magenta]Running allower evals...[/bold magenta]")
    await run_evals_allower()

    console.print("\n[bold magenta]Running orchestrator evals...[/bold magenta]")
    await run_evals_orchestrator()

    console.print("\n[bold magenta]Running summary evals...[/bold magenta]")
    await run_evals_summary()

    console.print("\n[bold magenta]Running question evals...[/bold magenta]")
    await run_evals_question()

    console.print("\n[bold magenta]Running article evals...[/bold magenta]")
    await run_evals_article()


if __name__ == "__main__":
    asyncio.run(main())
