import logging
from datetime import datetime

from pydantic import BaseModel, Field
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
    """
    The response of the orchestrator agent.
    It can be a summary of the latest articles, an answer to a question, or an article response.
    """

    type: str = Field(
        description="The type of the response. Can be 'summary', 'question_answer', or 'article'."
    )
    response: SummaryResponse | QuestionAnswerResponse | ArticleResponse = Field(
        description="The response to the request. It can be a summary of the latest articles,"
        + "an answer to a question, or an article response."
    )


orchestrator_agent_base = Agent(
    system_prompt=SYSTEM_PROMPT_ORCHESTRATOR,
    output_type=OrchestratorResponse,
    retries=20,
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
        orchestrator_agent_base.model_settings,
        query_list_limit=2,
        relevance_score_threshold=0.8,
        article_list_limit=2,
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

    article_agent = ArticleAgent(
        orchestrator_agent_base.model,
        orchestrator_agent_base.model_settings,
    )
    r = await article_agent.run(request=question)
    return r


if __name__ == "__main__":
    import asyncio

    from askademic.utils import choose_model

    model, model_settings = choose_model("claude-aws-bedrock")
    orchestrator_agent_base.model = model
    orchestrator_agent_base.model_settings = model_settings

    response = asyncio.run(
        orchestrator_agent_base.run("Can you summarize the latest papers on AI?")
    )
    print(response)
