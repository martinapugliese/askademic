"""
Checks that the is_scientific flag is set correctly.
"""

from rich.console import Console

from askademic.allower import allower_agent
from askademic.prompts import USER_PROMPT_ALLOWER_TEMPLATE


class AllowerTestCase:
    def __init__(self, question: str, is_scientic_gt: bool):
        self.question = question
        self.is_scientic_gt = is_scientic_gt


eval_cases = [
    AllowerTestCase("What is the latest research on quantum computing?", True),
    AllowerTestCase("Hello, how are you?", False),
    AllowerTestCase("Can you summarize the latest papers on AI?", True),
    AllowerTestCase("Tell me a joke about physics.", False),
    AllowerTestCase("What are the implications of quantum entanglement?", True),
    AllowerTestCase("What is the meaning of life?", False),
]

console = Console()


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        print(f"Evaluating case: {case.question}")
        response = await allower_agent.run(
            USER_PROMPT_ALLOWER_TEMPLATE.format(question=case.question)
        )

        if response.output.is_scientific != case.is_scientic_gt:
            print(f"Test failed for question: {case.question}")
            c_failed += 1
        else:
            c_passed += 1

    console.print(f"[bold cyan]Total cases: {len(eval_cases)}[/bold cyan]")
    if c_failed > 0:
        console.print(
            f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]")
