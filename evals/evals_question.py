"""
Checks response contains substring.
"""

from rich.console import Console

from askademic.prompts import USER_PROMPT_QUESTION_TEMPLATE
from askademic.question import question_agent


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


async def run_evals():

    c_passed, c_failed = 0, 0

    # single-answer ones
    for case in eval_cases_single:

        print(f"Evaluating case: {case.request}")
        response = await question_agent.run(
            USER_PROMPT_QUESTION_TEMPLATE.format(question=case.request)
        )

        if case.answer not in response.output.response:
            print(f"Test failed for question: {case.request}")
            print(f"Got: {response.output.response}")
            c_failed += 1
        else:
            c_passed += 1

    # cases that can have multiple close answers
    for case in eval_cases_range:

        print(f"Evaluating case: {case.request}")
        response = await question_agent.run(
            USER_PROMPT_QUESTION_TEMPLATE.format(question=case.request)
        )

        if (
            case.answer[0] not in response.output.response
            and case.answer[1] not in response.output.response
        ):
            print(f"Test failed for question: {case.request}")
            print(f"Got: {response.output.response}")
            c_failed += 1
        else:
            c_passed += 1

    tot = len(eval_cases_single) + len(eval_cases_range)
    console.print(f"[bold cyan]Total cases: {tot}[/bold cyan]")
    if c_failed > 0:
        console.print(
            f":check_mark: [bold green]Passed: {c_passed}[/bold green]"
            + ","
            + f":x: [bold red]Failed: {c_failed}[/bold red]"
        )
    console.print(f":check_mark: [bold green]Passed: {c_passed}[/bold green]")
