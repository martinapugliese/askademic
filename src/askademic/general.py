import logging
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.settings import ModelSettings

from askademic.prompts.general import SYSTEM_PROMPT_GENERAL
from askademic.tools import (
    get_article,
    get_categories,
    search_articles_by_abs,
    search_articles_by_title,
)

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class GeneralResponse(BaseModel):
    """The response for general academic requests that don't fit standard categories."""

    response: str = Field(description="The response to the academic request")
    sources_used: List[str] = Field(
        description="List of article links or sources used in the response", default=[]
    )
    suggested_followup: List[str] = Field(
        description="Suggested follow-up questions or actions", default=[]
    )
    confidence: str = Field(
        description="Confidence level: high, medium, or low", default="medium"
    )


general_agent_base = Agent(
    system_prompt=SYSTEM_PROMPT_GENERAL,
    output_type=GeneralResponse,
    retries=20,
    end_strategy="early",
)


class Context(BaseModel):
    pass


@general_agent_base.tool
async def search_papers_by_topic(
    ctx: RunContext[Context], topic: str, max_results: int = 10
) -> str:
    """
    Search for papers related to a topic by searching abstracts.
    Args:
        ctx: the context
        topic: The research topic or keywords to search for
        max_results: Maximum number of results to return
    """
    logger.info(f"{datetime.now()}: General agent searching for topic: {topic}")
    result = search_articles_by_abs(query=topic, max_results=max_results)
    return result


@general_agent_base.tool
async def search_papers_by_title_keyword(
    ctx: RunContext[Context], title_keywords: str, max_results: int = 10
) -> str:
    """
    Search for papers by title keywords.
    Args:
        ctx: the context
        title_keywords: Keywords that might appear in paper titles
        max_results: Maximum number of results to return
    """
    logger.info(
        f"{datetime.now()}: General agent searching titles for: {title_keywords}"
    )
    result = search_articles_by_title(query=title_keywords, max_results=max_results)
    return result


@general_agent_base.tool
async def get_paper_content(ctx: RunContext[Context], paper_url: str) -> str:
    """
    Retrieve the full content of a specific paper.
    Args:
        ctx: the context
        paper_url: The arXiv PDF URL of the paper
    """
    logger.info(f"{datetime.now()}: General agent retrieving paper: {paper_url}")
    result = get_article(url=paper_url)
    return result


@general_agent_base.tool
async def list_research_categories(ctx: RunContext[Context]) -> dict:
    """
    Get all available arXiv research categories.
    Args:
        ctx: the context
    """
    logger.info(f"{datetime.now()}: General agent listing categories")
    return get_categories()


class GeneralAgent:
    def __init__(self, model: str, model_settings: ModelSettings = None):
        self.agent = general_agent_base
        self.agent.model = model
        if model_settings:
            self.agent.model_settings = model_settings

    async def __call__(self, request: str) -> GeneralResponse:
        """
        Handle a general academic request.
        Args:
            request: The user's academic request
        """
        logger.info(
            f"{datetime.now()}: General agent handling request: {request[:100]}..."
        )

        result = await self.agent.run(request)
        return result.output
