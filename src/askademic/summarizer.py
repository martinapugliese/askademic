from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts import SYSTEM_PROMPT_SUMMARY
from askademic.tools import (
    get_categories,
    identify_latest_day,
    retrieve_recent_articles,
)


class Category(BaseModel):
    category_id: str = Field(description="The category ID of the topic requested.")
    category_name: str = Field(description="The category name of the topic requested.")


class SummaryResponse(BaseModel):
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


summary_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_SUMMARY,
    result_type=SummaryResponse,
    tools=[
        Tool(get_categories, takes_ctx=False),
        Tool(identify_latest_day, takes_ctx=False),
        Tool(retrieve_recent_articles, takes_ctx=False),
    ],
    model_settings={"max_tokens": 1000, "temperature": 0},
)
