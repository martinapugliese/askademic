from typing import Literal

import httpx
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, Tool

from constants import GEMINI_2_FLASH_MODEL_ID
from prompts import (  # SYSTEM_PROMPT_QUESTION,; SYSTEM_PROMPT_SUMMARY,
    SYSTEM_PROMPT_ORCHESTRATOR,
    SYSTEM_PROMPT_QUESTION,
    SYSTEM_PROMPT_SUMMARY,
    USER_PROMPT_QUESTION_TEMPLATE,
    USER_PROMPT_SUMMARY_TEMPLATE,
)
from tools import (
    choose_category,
    get_article,
    identify_latest_day,
    retrieve_recent_articles,
    search_articles,
)


class QuestionAnswerResponse(BaseModel):
    response: str = Field(description="The response to the question")
    article_list: list[str] = Field(
        description="The list of abstract/article urls you used to answer to the question."
    )
    source: Literal["abstracts", "articles"] = Field(
        description="Whether you found the answer in the abstracts or in the whole articles."
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


class Context(BaseModel):
    pass


summary_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_SUMMARY,
    result_type=SummaryResponse,
    tools=[
        Tool(choose_category, takes_ctx=False),
        Tool(identify_latest_day, takes_ctx=False),
        Tool(retrieve_recent_articles, takes_ctx=False),
    ],
    model_settings={"max_tokens": 1000, "temperature": 0},
)

question_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_QUESTION,
    result_type=QuestionAnswerResponse,
    tools=[
        Tool(search_articles, takes_ctx=False),
        Tool(get_article, takes_ctx=False),
    ],
    model_settings={"max_tokens": 1000, "temperature": 0},
)

orchestrator_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_ORCHESTRATOR,
    result_type=SummaryResponse | QuestionAnswerResponse,
    model_settings={"max_tokens": 1000, "temperature": 0},
)


@orchestrator_agent.tool
async def summarise_latest_articles(
    ctx: RunContext[Context], request: str
) -> list[str]:
    """
    Make a request to an agent about the most recent paper in a specific field.
    Args:
        ctx: the context
        request: the request
    """
    prompt = USER_PROMPT_SUMMARY_TEMPLATE.format(request=request)
    r = await summary_agent.run(prompt)
    return r


@orchestrator_agent.tool
async def answer_question(ctx: RunContext[Context], question: str) -> list[str]:
    """
    Ask an agent to search on arXiv and access articles to answer a question.
    Args:
        ctx: the context
        question: the question
    """

    prompt = USER_PROMPT_QUESTION_TEMPLATE.format(question=question)
    r = await question_agent.run(prompt)
    return r
