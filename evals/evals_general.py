"""
Evaluations for the general academic agent.
Tests flexibility, adaptability, and handling of diverse academic requests.
"""

import time
from typing import List

from rich.console import Console

from askademic.general import GeneralAgent
from askademic.utils import choose_model


class GeneralTestCase:
    def __init__(
        self,
        request: str,
        expected_keywords: List[str],
        description: str,
        min_confidence_threshold: str = "low",
    ):
        self.request = request
        self.expected_keywords = (
            expected_keywords  # Keywords that should appear in response
        )
        self.description = description
        self.min_confidence_threshold = min_confidence_threshold


class FlexibilityTestCase:
    def __init__(self, request: str, should_handle: bool, description: str):
        self.request = request
        self.should_handle = (
            should_handle  # Whether agent should successfully handle this
        )
        self.description = description


# Test cases for different types of academic requests
keyword_eval_cases = [
    GeneralTestCase(
        "How do I design a good research methodology for machine learning experiments?",
        ["methodology", "experiment", "design", "research", "machine learning"],
        "Research methodology guidance",
        "medium",
    ),
    GeneralTestCase(
        "What are the key principles of academic writing?",
        ["writing", "academic", "principles", "structure"],
        "Academic writing guidance",
        "high",
    ),
    GeneralTestCase(
        "Explain the concept of statistical significance in simple terms",
        ["statistical", "significance", "p-value", "hypothesis", "test"],
        "Concept explanation",
        "medium",
    ),
    GeneralTestCase(
        "What's the difference between quantitative and qualitative research methods?",
        ["quantitative", "qualitative", "research", "methods", "data"],
        "Methodological comparison",
        "high",
    ),
    GeneralTestCase(
        "How should I structure a literature review for my thesis?",
        ["literature", "review", "structure", "thesis", "sources"],
        "Academic guidance",
        "medium",
    ),
    GeneralTestCase(
        "What are some interdisciplinary approaches to studying climate change?",
        ["interdisciplinary", "climate", "approaches", "research"],
        "Interdisciplinary research",
        "medium",
    ),
    GeneralTestCase(
        "How do I choose the right statistical test for my data?",
        ["statistical", "test", "data", "analysis", "choose"],
        "Statistical guidance",
        "medium",
    ),
    GeneralTestCase(
        "What are the ethical considerations in AI research?",
        ["ethical", "AI", "research", "considerations", "bias"],
        "Ethics in research",
        "medium",
    ),
]

# Test cases for flexibility and edge case handling
flexibility_eval_cases = [
    FlexibilityTestCase(
        "I'm confused about which research paradigm to use for my sociology study",
        True,
        "Research paradigm guidance",
    ),
    FlexibilityTestCase(
        "Can you help me understand the peer review process?",
        True,
        "Academic process explanation",
    ),
    FlexibilityTestCase(
        "What are the current debates in computational linguistics?",
        True,
        "Field overview request",
    ),
    FlexibilityTestCase(
        "How do I deal with contradictory findings in my literature review?",
        True,
        "Academic problem-solving",
    ),
    FlexibilityTestCase(
        "What's the best way to present negative results in a research paper?",
        True,
        "Academic communication",
    ),
    FlexibilityTestCase(
        "I need help understanding Bayesian vs frequentist statistics",
        True,
        "Conceptual comparison",
    ),
    FlexibilityTestCase(
        "How do I write a compelling research proposal?",
        True,
        "Academic writing guidance",
    ),
    FlexibilityTestCase(
        "What are the emerging trends in data visualization for scientific papers?",
        True,
        "Current trends inquiry",
    ),
]

console = Console()
MAX_ATTEMPTS = 3


async def run_keyword_evals(model_family: str):
    """Test if general agent responses contain expected keywords"""

    model, model_settings = choose_model(model_family)
    general_agent = GeneralAgent(model, model_settings)

    c_passed, c_failed = 0, 0

    for case in keyword_eval_cases:
        time.sleep(2)
        attempt = 0

        while attempt < MAX_ATTEMPTS:
            try:
                console.print(f"[dim]Evaluating: {case.description}[/dim]")
                console.print(f"[dim]Request: {case.request[:60]}...[/dim]")

                response = await general_agent(case.request)

                # Check if response contains expected keywords
                response_text = response.response.lower()
                found_keywords = []
                missing_keywords = []

                for keyword in case.expected_keywords:
                    if keyword.lower() in response_text:
                        found_keywords.append(keyword)
                    else:
                        missing_keywords.append(keyword)

                # Pass if at least 60% of keywords are found
                keyword_score = len(found_keywords) / len(case.expected_keywords)

                if keyword_score >= 0.6:
                    console.print(
                        f"[green]✓ PASS[/green] - Found {len(found_keywords)}/{len(case.expected_keywords)} keywords"
                    )
                    c_passed += 1
                else:
                    console.print(
                        f"[red]✗ FAIL[/red] - Found {len(found_keywords)}/{len(case.expected_keywords)} keywords"
                    )
                    console.print(f"[dim]Missing: {missing_keywords}[/dim]")
                    c_failed += 1

                break

            except Exception as e:
                console.print(f"[yellow]Error: {e}[/yellow]")
                attempt += 1
                time.sleep(10)

                if attempt == MAX_ATTEMPTS:
                    console.print(
                        f"[red]Max attempts reached for: {case.description}[/red]"
                    )
                    c_failed += 1

    return c_passed, c_failed


async def run_flexibility_evals(model_family: str):
    """Test if general agent can handle diverse request types"""

    model, model_settings = choose_model(model_family)
    general_agent = GeneralAgent(model, model_settings)

    c_passed, c_failed = 0, 0

    for case in flexibility_eval_cases:
        time.sleep(2)
        attempt = 0

        while attempt < MAX_ATTEMPTS:
            try:
                console.print(f"[dim]Evaluating: {case.description}[/dim]")
                console.print(f"[dim]Request: {case.request[:60]}...[/dim]")

                response = await general_agent(case.request)

                # Check if agent provided a substantive response
                response_length = len(response.response.strip())
                has_sources = len(response.sources_used) > 0
                has_followup = len(response.suggested_followup) > 0

                # Pass if response is substantive (>100 chars) and shows engagement
                is_substantive = response_length > 100

                if case.should_handle:
                    if is_substantive:
                        console.print(
                            f"[green]✓ PASS[/green] - Substantive response ({response_length} chars)"
                        )
                        if has_sources:
                            console.print(
                                f"[dim]+ Used {len(response.sources_used)} sources[/dim]"
                            )
                        if has_followup:
                            console.print(
                                f"[dim]+ Provided {len(response.suggested_followup)} follow-ups[/dim]"
                            )
                        c_passed += 1
                    else:
                        console.print(
                            f"[red]✗ FAIL[/red] - Response too brief ({response_length} chars)"
                        )
                        c_failed += 1
                else:
                    # For cases that should not be handled well
                    if not is_substantive:
                        console.print(
                            "[green]✓ PASS[/green] - Appropriately brief response"
                        )
                        c_passed += 1
                    else:
                        console.print(
                            "[red]✗ FAIL[/red] - Should not have handled this well"
                        )
                        c_failed += 1

                break

            except Exception as e:
                console.print(f"[yellow]Error: {e}[/yellow]")
                attempt += 1
                time.sleep(10)

                if attempt == MAX_ATTEMPTS:
                    console.print(
                        f"[red]Max attempts reached for: {case.description}[/red]"
                    )
                    c_failed += 1

    return c_passed, c_failed


async def run_evals(model_family: str):
    """Run all general agent evaluations"""

    console.print(
        f"[bold blue]Running General Agent Evaluations for {model_family}[/bold blue]"
    )

    # Run keyword evaluations
    console.print("\n[bold cyan]Testing keyword relevance...[/bold cyan]")
    keyword_passed, keyword_failed = await run_keyword_evals(model_family)

    # Run flexibility evaluations
    console.print("\n[bold cyan]Testing flexibility and adaptability...[/bold cyan]")
    flex_passed, flex_failed = await run_flexibility_evals(model_family)

    # Summary
    total_passed = keyword_passed + flex_passed
    total_failed = keyword_failed + flex_failed
    total_cases = len(keyword_eval_cases) + len(flexibility_eval_cases)

    console.print("\n[bold magenta]General Agent Evaluation Summary[/bold magenta]")
    console.print(f"[bold cyan]Total cases: {total_cases}[/bold cyan]")
    console.print(f"[green]✓ Passed: {total_passed}[/green]")

    if total_failed > 0:
        console.print(f"[red]✗ Failed: {total_failed}[/red]")
        success_rate = (total_passed / total_cases) * 100
        console.print(f"[yellow]Success rate: {success_rate:.1f}%[/yellow]")
    else:
        console.print("[bold green]All tests passed! 🎉[/bold green]")
