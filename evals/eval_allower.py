import asyncio

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

    print(f"Total cases: {len(eval_cases)}")
    print(f"Passed: {c_passed}")
    print(f"Failed: {c_failed}")


def main():
    asyncio.run(run_evals())


if __name__ == "__main__":
    main()
