"""
Checks match link-title pairs by
searching first by title and then by link.
"""

import asyncio
import re

from askademic.article import article_agent
from askademic.prompts import USER_PROMPT_ARTICLE_TEMPLATE


class ArticleResponseTestCase:
    def __init__(self, request: str, article_data: str, title: str, link: str):
        self.request = request
        self.article_data = article_data
        self.title = title
        self.link = link


eval_cases = [
    ArticleResponseTestCase(
        "Tell me about paper 'Entity Embeddings of Categorical Variables'",
        "Entity Embeddings of Categorical Variables",
        "Entity Embeddings of Categorical Variables",
        "https://arxiv.org/pdf/1604.06737",
    ),
    ArticleResponseTestCase(
        "What is paper \
        'The deterministic Kermack-McKendrick model bounds the general stochastic epidemic' \
        about?",
        "The deterministic Kermack-McKendrick model bounds the general stochastic epidemic",
        "The deterministic Kermack-McKendrick model bounds the general stochastic epidemic",
        "https://arxiv.org/pdf/1602.01730",
    ),
    ArticleResponseTestCase(
        "Tell me about paper 'https://arxiv.org/pdf/1604.06737'",
        "https://arxiv.org/pdf/1604.06737",
        "Entity Embeddings of Categorical Variables",
        "https://arxiv.org/pdf/1604.06737",
    ),
    ArticleResponseTestCase(
        "What is paper https://arxiv.org/pdf/1602.01730 about?",
        "https://arxiv.org/pdf/1602.01730",
        "The deterministic Kermack-McKendrick model bounds the general stochastic epidemic",
        "https://arxiv.org/pdf/1602.01730",
    ),
]

# link found by LLM may have the optional v[x] version number at the end
# we want to match regardless
LINK_PATTERN = r"https?://arxiv\.org/pdf/(\d{4}\.\d{5})"


async def run_evals():

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        print(f"Evaluating case: {case.request}")
        response = await article_agent.run(
            USER_PROMPT_ARTICLE_TEMPLATE.format(
                question=case.request, article=case.article_data
            )
        )

        match1 = re.match(LINK_PATTERN, case.link)
        match2 = re.match(LINK_PATTERN, response.output.article_link)

        # check titles match (case insensitive), links regex match exists and are the same
        if (
            case.title.lower() != response.output.article_title.lower()
            or match1 is None
            or match2 is None
            or match1.group(1) != match2.group(1)
        ):
            print(f"Test failed for question: {case.request}")
            print(
                f"Got: {response.output.article_title} and {response.output.article_link}"
            )
            print(f"Expected: {case.title} and {case.link}")
            print("\n")
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
