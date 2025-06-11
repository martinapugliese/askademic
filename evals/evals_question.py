"""
Checks response contains substring.
"""

import time

from rich.console import Console

from askademic.question import QuestionAgent
from askademic.utils import choose_model


class QuestionAnswerTestCaseSingle:
    def __init__(self, request: str, answer: str):
        self.request = request
        self.answer = answer


class QuestionAnswerTestCaseRange:
    def __init__(self, request: str, answer: list[str]):
        self.request = request
        self.answer = answer


eval_cases_single = [
    QuestionAnswerTestCaseSingle("Who solved Fermat's last theorem?", "Andrew Wiles"),
    QuestionAnswerTestCaseSingle(
        "In which experimental framework did AlphaFold2 demonstrate \
                                 high capability in predicting protein structure?",
        "CASP14",
    ),
]

eval_cases_range = [
    QuestionAnswerTestCaseRange(
        "In which year did AlexNet come out?", ["2011", "2012"]
    ),
    QuestionAnswerTestCaseRange(
        "What percentage of DNA has been found to be shared between \
                                Sapiens and Neandertals?",
        ["4%", "5%"],
    ),
]

console = Console()

MAX_ATTEMPTS = 5


async def run_evals(model_family: str):

    c_passed, c_failed = 0, 0
    model, model_settings = choose_model(model_family)

    question_agent = QuestionAgent(
        model=model,
        model_settings=model_settings,
        query_list_limit=5,
        relevance_score_threshold=0.8,
        article_list_limit=3,
    )

    # single-answer ones
    for case in eval_cases_single:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")
                response = await question_agent(question=case.request)

                if case.answer not in response.output.response:
                    print(f"Test failed for question: {case.request}")
                    print(f"Got: {response.output.response}")
                    c_failed += 1
                else:
                    c_passed += 1
                attempt += 1
                break
            except Exception as e:
                print(f"Error: {e}")
                attempt += 1
                if attempt == MAX_ATTEMPTS:
                    print(f"Max attempts reached for question: {case.request}")
                    c_failed += 1

    # cases that can have multiple close answers
    for case in eval_cases_range:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")
                response = await question_agent(question=case.request)

                if (
                    case.answer[0] not in response.output.response
                    and case.answer[1] not in response.output.response
                ):
                    print(f"Test failed for question: {case.request}")
                    print(f"Got: {response.output.response}")
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

    tot = len(eval_cases_single) + len(eval_cases_range)
    console.print(f"[bold cyan]Total cases: {tot}[/bold cyan]")
    if c_failed > 0:
        console.print(
            f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":white_check_mark: [bold green]Passed: {c_passed}[/bold green]")
