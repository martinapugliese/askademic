"""
Checks match link-title pairs by
searching first by title and then by link.
"""

import re
import time

from rich.console import Console

from askademic.article import ArticleAgent
from askademic.utils import choose_model


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
        "https://arxiv.org/pdf/1602.01730.pdf",
        "THE DETERMINISTIC KERMACK-MCKENDRICK MODEL BOUNDS THE GENERAL STOCHASTIC EPIDEMIC",
        "https://arxiv.org/pdf/1602.01730.pdf",
    ),
    # not existing paper
    ArticleResponseTestCase(
        "Find this paper 'Quark Gluon plasma and AI'",
        "http://arxiv.org/pdf/2311.10621v2",
        "Hadronization of Heavy Quarks",
        "http://arxiv.org/pdf/2311.10621v2",
    ),
]

# link found by LLM may have the optional v[x] version number at the end
# we want to match regardless
LINK_PATTERN = r"https?://arxiv\.org/pdf/(?:\w+-\w+/)?(\d{4}\.\d{5}|[\w\-]+)"

console = Console()

MAX_ATTEMPTS = 5


async def run_evals(model_family: str):

    article_agent = ArticleAgent(model=choose_model(model_family))

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")
                response = await article_agent.run(request=case.request)

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
