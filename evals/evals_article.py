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
    def __init__(
        self,
        request: str,
        article_data: str,
        title: str,
        link: str,
        fuzzy_keywords: list[str] = None,
    ):
        self.request = request
        self.article_data = article_data
        self.title = title
        self.link = link
        # For fuzzy matching: if set, just check that response contains
        # at least one keyword and has a valid arXiv link format
        self.fuzzy_keywords = fuzzy_keywords


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
    # Fuzzy match: paper doesn't exist exactly, so we just check that a relevant
    # paper is returned (contains keywords) with a valid arXiv link
    ArticleResponseTestCase(
        "Find this paper 'Quark Gluon plasma and AI'",
        "",
        "",
        "",
        fuzzy_keywords=["quark", "gluon", "plasma", "qgp"],
    ),
]

# link found by LLM may have the optional v[x] version number at the end
# we want to match regardless
LINK_PATTERN = r"https?://arxiv\.org/pdf/(?:\w+-\w+/)?(\d{4}\.\d{5}|[\w\-]+)"

console = Console()

MAX_ATTEMPTS = 5


def check_fuzzy_match(case, response) -> tuple[bool, str]:
    """
    Check if response passes fuzzy matching criteria.
    Returns (passed, reason) tuple.
    """
    title = response.output.article_title.lower()
    link = response.output.article_link

    # Check for valid arXiv link format
    link_match = re.match(LINK_PATTERN, link)
    if link_match is None:
        return False, f"Invalid arXiv link format: {link}"

    # Check if at least one keyword is in the title
    keyword_found = any(kw.lower() in title for kw in case.fuzzy_keywords)
    if not keyword_found:
        return False, f"No keywords {case.fuzzy_keywords} found in title: {title}"

    return True, ""


def check_exact_match(case, response) -> tuple[bool, str]:
    """
    Check if response passes exact matching criteria.
    Returns (passed, reason) tuple.
    """
    match1 = re.match(LINK_PATTERN, case.link)
    match2 = re.match(LINK_PATTERN, response.output.article_link)

    # Check titles match (case insensitive)
    title_matches = case.title.lower().replace(
        "\n", " "
    ) == response.output.article_title.lower().replace("\n", " ")

    # Check links regex match exists and IDs are the same
    links_match = (
        match1 is not None and match2 is not None and match1.group(1) == match2.group(1)
    )

    if not title_matches or not links_match:
        reason = (
            f"Got: {response.output.article_title} and {response.output.article_link}\n"
            f"Expected: {case.title} and {case.link}"
        )
        return False, reason

    return True, ""


async def run_evals(model_family: str):

    model, model_settings = choose_model(model_family)
    article_agent = ArticleAgent(model=model, model_settings=model_settings)

    c_passed, c_failed = 0, 0
    for case in eval_cases:

        attempt = 0
        while attempt < MAX_ATTEMPTS:
            try:
                print(f"Evaluating case: {case.request}")
                response = await article_agent.run(request=case.request)

                # Use fuzzy matching if keywords are specified, else exact match
                if case.fuzzy_keywords:
                    passed, reason = check_fuzzy_match(case, response)
                else:
                    passed, reason = check_exact_match(case, response)

                if not passed:
                    print(f"Test failed for question: {case.request}")
                    print(reason)
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
