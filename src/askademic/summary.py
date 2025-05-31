import logging
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool

from askademic.prompts.general import (
    SYSTEM_PROMPT_CATEGORY,
    SYSTEM_PROMPT_SUMMARY,
    USER_PROMPT_CATEGORY_TEMPLATE,
    USER_PROMPT_SUMMARY_TEMPLATE,
)
from askademic.tools import (
    get_categories,
    identify_latest_day,
    retrieve_recent_articles,
)

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class Category(BaseModel):
    """The Arixv category of the topic better matching the request."""

    category_id: str = Field(description="The category ID of the topic requested.")
    category_name: str = Field(description="The category name of the topic requested.")


class Summary(BaseModel):
    """The summary of the articles requested."""

    summary: str = Field(
        description="Global summary of all abstracts, identifying topics."
    )


class SummaryResponse(BaseModel):
    """The response of the summary agent."""

    category: Category = Field(description="The category of the articles.")
    latest_published_day: str = Field(
        description="The latest day of publications available on the API."
    )
    summary: str = Field(
        description="Global summary of all abstracts, identifying topics."
    )
    recent_papers_url: str = Field(
        description="arXiv URL to the most recent papers in the chosen category"
    )


class SummaryAgent:
    def __init__(self, model):

        self._category_agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT_CATEGORY,
            output_type=Category,
            tools=[Tool(get_categories, takes_ctx=False)],
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._summary_agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT_SUMMARY,
            output_type=Summary,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._identify_latest_day = identify_latest_day
        self._retrieve_recent_articles = retrieve_recent_articles

    async def __call__(self, request: str) -> SummaryResponse:
        """
        Get the summary of the latest articles in a specific category.
        Args:
            request: the request to be evaluated
        Returns:
            summary: the summary of the latest articles in a specific category
        """
        # Get the category
        category = await self._category_agent.run(
            USER_PROMPT_CATEGORY_TEMPLATE.format(request=request)
        )

        logger.info(
            f"Category selected: {category.output.category_id} - {category.output.category_name}"
        )

        # Get the latest published day
        latest_day = self._identify_latest_day(category.output.category_id)

        # Get the articles
        articles = self._retrieve_recent_articles(
            category=category.output.category_id, latest_day=latest_day
        )

        logger.info(f"Latest published day: {latest_day} - Articles #: {len(articles)}")
        # logger.info(f"Articles: {articles}")

        # Create the summary
        summary = await self._summary_agent.run(
            USER_PROMPT_SUMMARY_TEMPLATE.format(articles=articles)
        )

        return SummaryResponse(
            category=category.output,
            latest_published_day=latest_day,
            summary=summary.output.summary,
            recent_papers_url=f"https://arxiv.org/list/{category.output.category_id}/new",
        )
