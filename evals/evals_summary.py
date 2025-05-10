"""
Checks category fetched is correct.
"""

import time

from rich.console import Console

from askademic.summary import summary_agent


class SummaryTestCase:
    def __init__(self, request: str, category: str):
        self.request = request
        self.category = category


eval_cases = [
    SummaryTestCase("What is the latest research on quantum field theory?", "hep-th"),
    SummaryTestCase("Can you summarize the latest papers on AI?", "cs.AI"),
    SummaryTestCase(
        "Tell me all about the recent work in Bayesian statistics?", "stat.TH"
    ),
]

console = Console()

MAX_ATTEMPTS = 5


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")
                response = await summary_agent(case.request)

                if response.category.category_id != case.category:
                    print(f"Test failed for question: {case.request}")
                    print(f"Got: {response.category.category_id}")
                    print(f"Expected: {case.category}")
                    c_failed += 1
                else:
                    c_passed += 1
                attempt += 1
                break
            except Exception as e:
                print(f"Error: {e}")
                attempt += 1
                time.sleep(20)
                if attempt == MAX_ATTEMPTS:
                    print(f"Max attempts reached for question: {case.request}")

    console.print(f"[bold cyan]Total cases: {len(eval_cases)}[/bold cyan]")
    if c_failed > 0:
        console.print(
            f":check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":check_mark: [bold green]Passed: {c_passed}[/bold green]")
