from pydantic import BaseModel, Field
from pydantic_ai import Agent, Tool

from askademic.prompts.general import SYSTEM_PROMPT_ARTICLE
from askademic.tools import get_article, search_articles_by_title


class ArticleResponse(BaseModel):
    response: str = Field(description="The response to the question")
    article_title: str = Field(
        description="The title of the article you used to answer the question."
    )
    article_link: str = Field(
        description="The article link you used to answer the question."
    )


article_agent_base = Agent(
    system_prompt=SYSTEM_PROMPT_ARTICLE,
    output_type=ArticleResponse,
    tools=[
        Tool(search_articles_by_title, takes_ctx=False),
        Tool(get_article, takes_ctx=False),
    ],
    model_settings={"max_tokens": 1000, "temperature": 0},
    end_strategy="early",
)
