"""
Checks category fetched is correct.
"""

import asyncio

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

    print(f"Total cases: {len(eval_cases)}")
    print(f"Passed: {c_passed}")
    print(f"Failed: {c_failed}")


def main():
    asyncio.run(run_evals())


if __name__ == "__main__":
    main()
