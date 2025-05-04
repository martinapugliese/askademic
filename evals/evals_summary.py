import asyncio

from askademic.prompts import USER_PROMPT_ALLOWER_TEMPLATE
from askademic.summarizer import summary_agent


class SummaryTestCase:
    def __init__(self, request: str, is_scientic_gt: bool):
        self.request = request
        self.is_scientic_gt = is_scientic_gt


eval_cases = [
    SummaryTestCase("What is the latest research on particle physics?", "hep-ex"),
    SummaryTestCase("Can you summarize the latest papers on AI?", "cs.AI"),
]


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        print(f"Evaluating case: {case.request}")
        response = await summary_agent.run(
            USER_PROMPT_ALLOWER_TEMPLATE.format(question=case.request)
        )

        if response.output.is_scientific != case.is_scientic_gt:
            print(f"Test failed for question: {case.request}")
            c_failed += 1
        else:
            c_passed += 1

    print(f"Total cases: {len(eval_cases)}")
    print(f"Passed: {c_passed}")
    print(f"Failed: {c_failed}")


def main():
    asyncio.run(run_evals())


if __name__ == "__main__":
    main()
