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
]


async def run_evals():

    for case in eval_cases:

        print(f"Evaluating case: {case.question}")
        response = await allower_agent.run(
            USER_PROMPT_ALLOWER_TEMPLATE.format(question=case.question)
        )
        print(f"Response: {response}")

        if response.output.is_scientific != case.is_scientic_gt:
            print(f"Test failed for question: {case.question}")
            print(
                f"Expected: {case.is_scientic_gt}, Got: {response.output.is_scientific}"
            )
        else:
            print(f"Test passed for question: {case.question}")


def main():
    asyncio.run(run_evals())


if __name__ == "__main__":
    main()
