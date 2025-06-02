import logging
from datetime import datetime

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from askademic.article import ArticleAgent, ArticleResponse
from askademic.prompts.general import SYSTEM_PROMPT_ORCHESTRATOR
from askademic.question import QuestionAgent, QuestionAnswerResponse
from askademic.summary import SummaryAgent, SummaryResponse

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class Context(BaseModel):
    pass


class OrchestratorResponse(BaseModel):
    """The response of the orchestrator agent."""

    BaseModel: SummaryResponse | QuestionAnswerResponse | ArticleResponse


orchestrator_agent_base = Agent(
    system_prompt=SYSTEM_PROMPT_ORCHESTRATOR,
    output_type=OrchestratorResponse,
    model_settings={"max_tokens": 1000, "temperature": 0},
    end_strategy="early",
)


@orchestrator_agent_base.tool
async def summarise_latest_articles(
    ctx: RunContext[Context], request: str
) -> list[str]:
    """
    Make a request to an agent about the most recent paper in a specific field.
    Args:
        ctx: the context
        request: the request
    """
    logger.info(f"{datetime.now()}: Calling Summary Agent with request: {request}")
    summary_agent = SummaryAgent(orchestrator_agent_base.model)
    r = await summary_agent(request=request)
    logger.info(f"{datetime.now()}: got reponse {r};)")

    return r


@orchestrator_agent_base.tool
async def answer_question(ctx: RunContext[Context], question: str) -> list[str]:
    """
    Ask an agent to search on arXiv and access articles to answer a question.
    Args:
        ctx: the context
        question: the question
    """
    logger.info(f"{datetime.now()}: Calling QA Agent with question: {question}")
    question_agent = QuestionAgent(
        orchestrator_agent_base.model,
        query_list_limit=5,
        relevance_score_threshold=0.8,
        article_list_limit=3,
    )
    r = await question_agent(question=question)
    return r


@orchestrator_agent_base.tool
async def answer_article(ctx: RunContext[Context], question: str) -> list[str]:
    """
    Ask an agent to retrieve an article based on its title, link or arxiv id.
    Then, ask the agent to read the article and answer a question.
    Args:
        ctx: the context
        question: the question
    Returns:
        r: the response from the agent
    If the response says that the article is not found, the requested article is not available
    on arXiv.
    """
    logger.info(f"{datetime.now()}: Calling Article Agent with question {question};)")

    article_agent = ArticleAgent(orchestrator_agent_base.model)
    r = await article_agent.run(request=question)
    return r
