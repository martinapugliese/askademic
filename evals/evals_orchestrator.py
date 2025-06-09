"""
Checks delegation to right agent via type of response.
"""

import time

from pydantic_ai.usage import UsageLimits
from rich.console import Console

from askademic.article import ArticleResponse
from askademic.orchestrator import orchestrator_agent_base
from askademic.question import QuestionAnswerResponse
from askademic.summary import SummaryResponse
from askademic.utils import choose_model


class OrchestratorTestCase:
    def __init__(
        self,
        request: str,
        response_type: SummaryResponse | QuestionAnswerResponse | ArticleResponse,
    ):
        self.request = request
        self.response_type = response_type


eval_cases = [
    OrchestratorTestCase(
        "What is the latest research on quantum computing?", SummaryResponse
    ),
    OrchestratorTestCase("Can you summarize the latest papers on AI?", SummaryResponse),
    OrchestratorTestCase(
        "What's the relation between context length and quality in LLM performance?",
        QuestionAnswerResponse,
    ),
    OrchestratorTestCase(
        "Tell me all about the paper 'Attention is all you need'", ArticleResponse
    ),
]

console = Console()

MAX_ATTEMPTS = 5


async def run_evals(model_family: str):

    orchestrator_agent = orchestrator_agent_base
    model, model_settings = choose_model(model_family)
    orchestrator_agent.model = model
    orchestrator_agent.model_settings = model_settings

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        time.sleep(2)
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")

                response = await orchestrator_agent.run(
                    case.request,
                    usage_limits=UsageLimits(request_limit=20),  # limit requests
                )

                if not isinstance(response.output.response, case.response_type):
                    print(f"Test failed for question: {case.request}")
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
