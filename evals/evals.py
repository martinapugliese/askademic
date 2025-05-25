import asyncio

from evals_allower import run_evals as run_evals_allower
from evals_article import run_evals as run_evals_article
from evals_orchestrator import run_evals as run_evals_orchestrator
from evals_question import run_evals as run_evals_question
from evals_summary import run_evals as run_evals_summary
from rich.console import Console

console = Console()


async def main():

    for model_family in ["gemini", "claude"]:

        console.print(
            f"[bold cyan]:hourglass: Running all evals for {model_family}...[/bold cyan]"
        )

        await run_evals_allower(model_family)

        console.print("\n[bold magenta]Running orchestrator evals...[/bold magenta]")
        await run_evals_orchestrator(model_family)

        console.print("\n[bold magenta]Running summary evals...[/bold magenta]")
        await run_evals_summary(model_family)

        console.print("\n[bold magenta]Running question evals...[/bold magenta]")
        await run_evals_question(model_family)

        console.print("\n[bold magenta]Running article evals...[/bold magenta]")
        await run_evals_article(model_family)


if __name__ == "__main__":
    asyncio.run(main())
