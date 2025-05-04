"""
Checks delegation to right agent via type of response.
"""

from rich.console import Console

from askademic.article import ArticleResponse
from askademic.orchestrator import orchestrator_agent
from askademic.question import QuestionAnswerResponse
from askademic.summarizer import SummaryResponse


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
        "Tell me all about paper 'Attention is all you need'", ArticleResponse
    ),
]

console = Console()


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        print(f"Evaluating case: {case.request}")
        response = await orchestrator_agent.run(case.request)

        if not isinstance(response.output, case.response_type):
            print(f"Test failed for question: {case.request}")
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
