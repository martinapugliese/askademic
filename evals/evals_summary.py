"""
Checks category fetched is correct.
"""

import os
import time
from typing import List

import logfire
from dotenv import load_dotenv
from rich.console import Console

from askademic.summary import SummaryAgent
from askademic.utils import choose_model

# Load environment and configure logfire
load_dotenv()
logfire_token = os.getenv("LOGFIRE_TOKEN", None)
if logfire_token:
    logfire.configure(token=logfire_token, console=False)
    logfire.instrument_pydantic_ai()


class SummaryTestCase:
    def __init__(self, request: str, category_list: List[str]):
        self.request = request
        self.category_list = category_list


eval_cases = [
    SummaryTestCase("What is the latest research on quantum field theory?", ["hep-th"]),
    SummaryTestCase("Can you summarize the latest papers on AI?", ["cs.AI"]),
    SummaryTestCase(
        "Tell me all about the recent work in Bayesian statistics?",
        ["stat.TH", "stat.ME"],
    ),
]

console = Console()

MAX_ATTEMPTS = 5


async def run_evals(model_family: str):

    model, model_settings = choose_model(model_family)
    summary_agent = SummaryAgent(model=model, model_settings=model_settings)

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")

                response = await summary_agent(case.request)
                if response.category.category_id not in case.category_list:
                    print(f"Test failed for question: {case.request}")
                    print(f"Got: {response.category.category_id}")
                    print(f"Expected: {case.category_list}")
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
            f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]")
