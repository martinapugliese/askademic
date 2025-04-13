from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts import SYSTEM_PROMPT_QUESTION
from askademic.tools import get_article, search_articles


class QuestionAnswerResponse(BaseModel):
    response: str = Field(description="The response to the question")
    article_list: list[str] = Field(
        description="The list of abstract/article urls you used to answer to the question."
    )
    source: Literal["abstracts", "articles"] = Field(
        description="Whether you found the answer in the abstracts or in the whole articles."
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
