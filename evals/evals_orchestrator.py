"""
Checks delegation to right agent via type of response.
"""

import os
import time

import logfire
from dotenv import load_dotenv
from pydantic_ai.usage import UsageLimits
from rich.console import Console

from askademic.article import ArticleResponse
from askademic.general import GeneralResponse
from askademic.orchestrator import orchestrator_agent_base
from askademic.question import QuestionAnswerResponse
from askademic.summary import SummaryResponse
from askademic.utils import choose_model

# Load environment and configure logfire
load_dotenv()
logfire_token = os.getenv("LOGFIRE_TOKEN", None)
if logfire_token:
    logfire.configure(token=logfire_token, console=False)
    logfire.instrument_pydantic_ai()


class OrchestratorTestCase:
    def __init__(
        self,
        request: str,
        response_type: (
            SummaryResponse | QuestionAnswerResponse | ArticleResponse | GeneralResponse
        ),
    ):
        self.request = request
        self.response_type = response_type


eval_cases = [
    # Summary routing tests
    OrchestratorTestCase(
        "What is the latest research on quantum computing?", SummaryResponse
    ),
    OrchestratorTestCase("Can you summarize the latest papers on AI?", SummaryResponse),
    # Question answering routing tests
    OrchestratorTestCase(
        "What's the relation between context length and quality in LLM performance?",
        QuestionAnswerResponse,
    ),
    # Article routing tests
    OrchestratorTestCase(
        "Tell me all about the paper 'Attention is all you need'", ArticleResponse
    ),
    # General academic routing tests - these should route to general_academic
    OrchestratorTestCase(
        "How do I design a good research methodology?", GeneralResponse
    ),
    OrchestratorTestCase(
        "What are the key principles of academic writing?", GeneralResponse
    ),
    OrchestratorTestCase(
        "Explain the concept of statistical significance", GeneralResponse
    ),
    OrchestratorTestCase(
        "What's the difference between quantitative and qualitative research?",
        GeneralResponse,
    ),
    OrchestratorTestCase(
        "How should I structure a literature review?", GeneralResponse
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
