import logging
import re
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import UsageLimits

from askademic.prompts.general import SYSTEM_PROMPT_QUESTION_AGENT
from askademic.tools import get_article, search_articles_by_abs

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class QuestionAnswerResponse(BaseModel):
    """The response to the question based on the articles."""

    response: str = Field(description="The response to the question")
    article_list: list[str] = Field(
        description="The list of article URLs you used to answer the question."
    )


class QuestionAgentDeps(BaseModel):
    """Dependencies for the question agent."""

    use_cache: bool = True


class QuestionAgent:
    def __init__(
        self,
        model: str,
        model_settings: ModelSettings = None,
        use_cache: bool = True,
    ):
        """
        Initialize the QuestionAgent.

        Args:
            model: The model to use for the agent.
            model_settings: Optional model settings.
            use_cache: Whether to use cached articles. Default is True.
        """
        self.use_cache = use_cache

        self._agent = Agent(
            model=model,
            model_settings=model_settings,
            system_prompt=SYSTEM_PROMPT_QUESTION_AGENT,
            output_type=QuestionAnswerResponse,
            deps_type=QuestionAgentDeps,
        )

        @self._agent.tool
        def search_articles(ctx: RunContext[QuestionAgentDeps], query: str) -> str:
            """
            Search arXiv for articles by searching in their abstracts.
            Returns a JSON string with article links and abstracts.

            Args:
                query: The search query to find relevant articles.
            Returns:
                A JSON string containing a list of articles with their links and abstracts.
            """
            logger.info(f"{datetime.now()}: Searching articles with query: {query}")
            result = search_articles_by_abs(query)
            logger.info(f"{datetime.now()}: Search results: {result[:200]}...")
            return result

        @self._agent.tool
        def fetch_article(ctx: RunContext[QuestionAgentDeps], link: str) -> str:
            """
            Fetch the full content of an article from arXiv.

            Args:
                link: The arXiv link or ID (e.g., "https://arxiv.org/abs/1706.03762"
                      or "1706.03762" or "https://arxiv.org/pdf/1706.03762.pdf").
            Returns:
                The full text content of the article.
            """
            normalized_link = self._normalize_arxiv_link(link)
            logger.info(f"{datetime.now()}: Fetching article: {normalized_link}")
            result = get_article(normalized_link, use_cache=ctx.deps.use_cache)
            logger.info(f"{datetime.now()}: Article fetched, length: {len(result)}")
            return result

    def _normalize_arxiv_link(self, link: str) -> str:
        """
        Normalize various arXiv link formats to PDF URL.

        Handles:
        - Full PDF URL: https://arxiv.org/pdf/1706.03762.pdf
        - Abstract URL: https://arxiv.org/abs/1706.03762
        - Just the ID: 1706.03762 or 2401.00001
        """
        if link.endswith(".pdf"):
            return link

        arxiv_id = None
        id_pattern = r"(\d{4}\.\d{4,5})"

        if "arxiv.org" in link:
            match = re.search(id_pattern, link)
            if match:
                arxiv_id = match.group(1)
        else:
            match = re.match(id_pattern, link.strip())
            if match:
                arxiv_id = match.group(1)

        if arxiv_id:
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        return link

    async def run(self, question: str):
        """
        Run the question agent to answer a research question.

        Args:
            question: The research question to answer.

        Returns:
            The agent result with the answer and list of article URLs used.
        """
        logger.info(f"{datetime.now()}: QuestionAgent received question: {question}")

        deps = QuestionAgentDeps(use_cache=self.use_cache)
        usage_limits = UsageLimits(tool_calls_limit=20)
        result = await self._agent.run(question, deps=deps, usage_limits=usage_limits)

        logger.info(f"{datetime.now()}: QuestionAgent completed question")
        return result

    async def __call__(self, question: str):
        """Alias for run() to maintain backward compatibility."""
        return await self.run(question)
