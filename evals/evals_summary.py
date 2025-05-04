"""
Checks category fetched is correct.
"""

from rich.console import Console

from askademic.summarizer import summary_agent


class SummaryTestCase:
    def __init__(self, request: str, category: str):
        self.request = request
        self.category = category


eval_cases = [
    SummaryTestCase("What is the latest research on particle physics?", "hep-ex"),
    SummaryTestCase("Can you summarize the latest papers on AI?", "cs.AI"),
    SummaryTestCase("Tell me all about the recent work in probability?", "stat.TH"),
]

console = Console()


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        print(f"Evaluating case: {case.request}")
        response = await summary_agent(request=case.request)

        if response.category != case.category:
            print(f"Test failed for question: {case.request}")
            c_failed += 1
        else:
            c_passed += 1

    console.print(f"[bold cyan]Total cases: {len(eval_cases)}[/bold cyan]")
    if c_failed > 0:
        console.print(
            f":check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":check_mark: [bold green]Passed: {c_passed}[/bold green]")
