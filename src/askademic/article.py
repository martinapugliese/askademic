import logging
import re
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings

from askademic.prompts.general import SYSTEM_PROMPT_ARTICLE_AGENT
from askademic.tools import get_article, search_articles_by_title

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class ArticleResponse(BaseModel):
    """
    The response to the article agent.
    It contains the response to the request, the article title and the article link.
    """

    response: str = Field(description="The response to the request")
    article_title: str = Field(
        description="The title of the article you used to answer the request."
    )
    article_link: str = Field(
        description="The article link you used to answer the request."
    )


class ArticleAgentDeps(BaseModel):
    """Dependencies for the article agent."""

    use_cache: bool = True


class ArticleAgent:
    def __init__(
        self, model: str, model_settings: ModelSettings = None, use_cache: bool = True
    ):
        self.use_cache = use_cache

        self._agent = Agent(
            model=model,
            model_settings=model_settings,
            system_prompt=SYSTEM_PROMPT_ARTICLE_AGENT,
            output_type=ArticleResponse,
            deps_type=ArticleAgentDeps,
        )

        @self._agent.tool
        def search_by_title(ctx: RunContext[ArticleAgentDeps], title: str) -> str:
            """
            Search arXiv for articles matching a title.
            Returns a JSON string with article links and abstracts.

            Args:
                title: The title or keywords to search for.
            """
            logger.info(f"{datetime.now()}: Searching articles by title: {title}")
            result = search_articles_by_title(title)
            logger.info(f"{datetime.now()}: Search results: {result[:200]}...")
            return result

        @self._agent.tool
        def fetch_article(ctx: RunContext[ArticleAgentDeps], link: str) -> str:
            """
            Fetch the full content of an article from arXiv.

            Args:
                link: The arXiv link or ID (e.g., "https://arxiv.org/abs/1706.03762"
                      or "1706.03762" or "https://arxiv.org/pdf/1706.03762.pdf").
            """
            # Normalize the link to PDF format
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
        # If it's already a PDF link, return as-is
        if link.endswith(".pdf"):
            return link

        # Extract arxiv ID from various formats
        arxiv_id = None

        # Pattern for arxiv ID (old format: YYMM.NNNNN or new format: YYMM.NNNNN)
        id_pattern = r"(\d{4}\.\d{4,5})"

        if "arxiv.org" in link:
            # Extract ID from URL
            match = re.search(id_pattern, link)
            if match:
                arxiv_id = match.group(1)
        else:
            # Assume it's just the ID
            match = re.match(id_pattern, link.strip())
            if match:
                arxiv_id = match.group(1)

        if arxiv_id:
            return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        # If we couldn't parse it, return as-is and let the downstream handle the error
        return link

    async def run(self, request: str):
        """
        Run the article agent to answer a question about an article.

        Args:
            request: The question to answer, which should reference an article
                     by title, link, or arXiv ID.

        Returns:
            The agent result with normalized article_link in PDF format.
        """
        logger.info(f"{datetime.now()}: ArticleAgent received request: {request}")

        deps = ArticleAgentDeps(use_cache=self.use_cache)
        result = await self._agent.run(request, deps=deps)

        # Normalize the article_link to PDF format in the output
        if result.output and result.output.article_link:
            normalized_link = self._normalize_arxiv_link(result.output.article_link)
            result.output.article_link = normalized_link

        logger.info(f"{datetime.now()}: ArticleAgent completed request")
        return result
