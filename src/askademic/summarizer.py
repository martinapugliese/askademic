import asyncio

import nest_asyncio
from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts import (
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

nest_asyncio.apply()  # Allows nesting of event loops


class Category(BaseModel):
    category_id: str = Field(description="The category ID of the topic requested.")
    category_name: str = Field(description="The category name of the topic requested.")


class Summary(BaseModel):
    summary: str = Field(
        description="Global summary of all abstracts, identifying topics."
    )


class SummaryResponse(BaseModel):
    category: Category = Field(description="The category of the articles.")
    latest_published_day: str = Field(
        description="The latest day of publications available on the API."
    )
    summary: Summary = Field(
        description="Global summary of all abstracts, identifying topics."
    )
    recent_papers_url: str = Field(
        description="arXiv URL to the most recent papers in the chosen category"
    )


class SummaryAgent:
    def __init__(self):

        self._category_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_CATEGORY,
            result_type=Category,
            tools=[Tool(get_categories, takes_ctx=False)],
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._summary_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_SUMMARY,
            result_type=Summary,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

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

        # Get the latest published day
        latest_day = identify_latest_day(category.data.category_id)

        # Get the articles
        articles = retrieve_recent_articles(
            category=category.data.category_id, latest_day=latest_day
        )

        # Create the summary
        summary = await self._summary_agent.run(
            USER_PROMPT_SUMMARY_TEMPLATE.format(articles=articles)
        )

        return SummaryResponse(
            category=category.data,
            latest_published_day=latest_day,
            summary=summary.data,
            recent_papers_url=f"https://arxiv.org/list/{category.data.category_id}/new",
        )


summary_agent = SummaryAgent()


# Example usage: Remove this part in production
async def main():
    summary = await summary_agent(
        "What are the latest advancements in quantum computing?"
    )
    print(summary)


if __name__ == "__main__":
    asyncio.run(main())
