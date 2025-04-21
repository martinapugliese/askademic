import logging
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from askademic.article import ArticleResponse, article_agent
from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts import (
    SYSTEM_PROMPT_ORCHESTRATOR,
    USER_PROMPT_ARTICLE_TEMPLATE,
    USER_PROMPT_QUESTION_TEMPLATE,
)
from askademic.question import QuestionAnswerResponse, question_agent
from askademic.summarizer import SummaryResponse, summary_agent

today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"{today}_logs.txt")
logger = logging.getLogger(__name__)


class Context(BaseModel):
    pass


orchestrator_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_ORCHESTRATOR,
    output_type=SummaryResponse | QuestionAnswerResponse | ArticleResponse,
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
    logger.info(f"{datetime.now()}: Calling Summary Agent with this request: {request}")
    r = await summary_agent(request=request)
    return r


@orchestrator_agent.tool
async def answer_question(ctx: RunContext[Context], question: str) -> list[str]:
    """
    Ask an agent to search on arXiv and access articles to answer a question.
    Args:
        ctx: the context
        question: the question
    """
    logger.info(f"{datetime.now()}: Calling QA Agent with this question: {question}")
    prompt = USER_PROMPT_QUESTION_TEMPLATE.format(question=question)
    r = await question_agent.run(prompt)
    return r


@orchestrator_agent.tool
async def answer_article(
    ctx: RunContext[Context], article: str, question: str
) -> list[str]:
    """
    Ask an agent to retrieve an article based on its title, link or arxiv id.
    Then, ask the agent to read the article and answer a question.
    Args:
        ctx: the context
        article: the article title, link or article id
        question: the question
    """
    logger.info(
        f"{datetime.now()}: Calling Article Agent with this question and: {question}  (article: {article})"
    )
    prompt = USER_PROMPT_ARTICLE_TEMPLATE.format(question=question, article=article)
    r = await article_agent.run(prompt)
    return r
