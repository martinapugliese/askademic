import logging
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts.general import (
    SYSTEM_PROMPT_ABSTRACT_RELEVANCE,
    SYSTEM_PROMPT_MANY_ARTICLES,
    SYSTEM_PROMPT_QUERY,
    USER_PROMPT_ABSTRACT_RELEVANCE_TEMPLATE,
    USER_PROMPT_MANY_ARTICLES_TEMPLATE,
    USER_PROMPT_QUERY_TEMPLATE,
)
from askademic.tools import get_article, search_articles_by_abs

# from askademic.prompts.claude import (
#     SYSTEM_PROMPT_MANY_ARTICLES,
#     USER_PROMPT_MANY_ARTICLES,
# )


today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class QueryResponse(BaseModel):
    queries: list[str] = Field(description="The list of queries to search for articles")


class Article(BaseModel):
    article_url: str = Field(description="The url to the article")
    relevance_score: float = Field(
        description="The relevance score of the article to the question"
    )


class ArticleListResponse(BaseModel):
    article_list: list[Article] = Field(
        description="The list of articles needed to answer the question."
    )


class QuestionAnswerResponse(BaseModel):
    response: str = Field(description="The response to the question")
    article_list: list[str] = Field(
        description="The list of abstract/article urls you used to answer to the question."
    )


class QuestionAgent:
    def __init__(
        self,
        query_list_limit: int = 10,
        relevance_score_threshold: float = 0.8,
        article_list_limit: int = 10,
    ):
        """
        Initialize the QuestionAgent with the query list limit.
        Args:
            query_list_limit (int): The maximum number of queries to generate.
        """

        self._query_list_limit = query_list_limit
        self._relevance_score_threshold = relevance_score_threshold
        self._article_list_limit = article_list_limit
        self._search_articles_by_abs = search_articles_by_abs
        self._get_article = get_article

        self._query_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_QUERY,
            output_type=QueryResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._abstract_relevance_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_ABSTRACT_RELEVANCE,
            output_type=ArticleListResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._many_articles_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_MANY_ARTICLES,
            output_type=QuestionAnswerResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

    async def __call__(self, question: str) -> QuestionAnswerResponse:

        # Generate Queries
        query_list = await self._query_agent.run(
            USER_PROMPT_QUERY_TEMPLATE.format(question=question),
        )

        # Retrieve abstract lists
        abstract_list = [
            self._search_articles_by_abs(query)
            for query in query_list.output.queries[: self._query_list_limit]
        ]

        # Filter relevant abstracts
        article_link_list = []
        for abstracts in abstract_list:
            article_link_list_tmp = await self._abstract_relevance_agent.run(
                USER_PROMPT_ABSTRACT_RELEVANCE_TEMPLATE.format(
                    question=question, abstracts=abstracts
                ),
            )
            article_link_list += list(article_link_list_tmp.output.article_list)

        logger.info("article_link_list: %s", article_link_list)

        # Filter the article list based on the relevance score threshold
        article_link_list = [
            article.article_url
            for article in article_link_list
            if article.relevance_score >= self._relevance_score_threshold
        ]

        logger.info("article_link_list after filtering: %s", article_link_list)

        article_link_list = article_link_list[: self._article_list_limit]
        article_list = [self._get_article(article) for article in article_link_list]
        article_list = "\n".join(article_list)

        # Use the article list to answer the question
        question_answer = await self._many_articles_agent.run(
            USER_PROMPT_MANY_ARTICLES_TEMPLATE.format(
                question=question, articles=article_list
            ),
        )

        return question_answer


question_agent = QuestionAgent(
    query_list_limit=5,
    relevance_score_threshold=0.8,
    article_list_limit=5,
)
