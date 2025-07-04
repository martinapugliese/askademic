import logging
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings

from askademic.prompts.general import (
    SYSTEM_PROMPT_ARTICLE,
    SYSTEM_PROMPT_ARTICLE_RETRIEVAL,
    SYSTEM_PROMPT_REQUEST_DISCRIMINATOR,
    USER_PROMPT_ARTICLE_RETRIEVAL_TEMPLATE,
    USER_PROMPT_ARTICLE_TEMPLATE,
    USER_PROMPT_REQUEST_DISCRIMINATOR_TEMPLATE,
)
from askademic.tools import get_article, search_articles_by_title

today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(level=logging.INFO, filename=f"logs/{today}_logs.txt")
logger = logging.getLogger(__name__)


class ArticleRequestDiscriminatorResponse(BaseModel):
    """
    The response to the article request discriminator agent.
    It contains the type of article request and the value of the article.
    """

    article_type: str = Field(
        description="The type of article request: 'title', 'link', or 'error'."
    )
    article_value: str = Field(
        description="The article title, link or an emtpy string if the type is error."
    )


class ArticleResponse(BaseModel):
    """
    The response to the article agent.
    It contains the response to the request, the article title and the article link.
    """

    response: str = Field(description="The response to the request")
    article_title: str = Field(
        description="The title of the article you used to answer the request."
    )
    article_link: str = Field(
        description="The article link you used to answer the request."
    )


class ArticleRetrievalResponse(BaseModel):
    """
    The response to the article retrieval agent.
    It contains the article link and title.
    """

    article_link: str = Field(description="The article link you found.")
    article_title: str = Field(description="The title of the article you found.")


class ArticleAgent:
    def __init__(self, model: Model, model_settings: ModelSettings = None, use_cache: bool = True):

        self._get_article = get_article
        self.use_cache = use_cache
        self._search_articles_by_title = search_articles_by_title

        self._article_request_discriminator_agent = Agent(
            model=model,
            model_settings=model_settings,
            system_prompt=SYSTEM_PROMPT_REQUEST_DISCRIMINATOR,
            output_type=ArticleRequestDiscriminatorResponse,
        )

        self._article_agent = Agent(
            model=model,
            model_settings=model_settings,
            system_prompt=SYSTEM_PROMPT_ARTICLE,
            output_type=ArticleResponse,
        )

        self._article_retrieval_agent = Agent(
            model=model,
            model_settings=model_settings,
            system_prompt=SYSTEM_PROMPT_ARTICLE_RETRIEVAL,
            output_type=ArticleRetrievalResponse,
        )

    async def _discriminate_article_request(
        self, request: str
    ) -> ArticleRequestDiscriminatorResponse:
        """
        Discriminate the type of article request.
        Args:
            request: the request to discriminate
        Returns:
            ArticleRequestDiscriminatorResponse: the response with the article type and value
        """
        return await self._article_request_discriminator_agent.run(
            USER_PROMPT_REQUEST_DISCRIMINATOR_TEMPLATE.format(request=request)
        )

    async def _retrieve_article(self, article_title: str) -> ArticleRetrievalResponse:
        """
        Retrieve an article link by its title.
        Args:
            article_title: the title of the article to retrieve
        Returns:
            ArticleRetrievalResponse: the response with the article link and title
        """
        articles = self._search_articles_by_title(article_title)

        return await self._article_retrieval_agent.run(
            USER_PROMPT_ARTICLE_RETRIEVAL_TEMPLATE.format(
                article_title=article_title, articles=articles
            )
        )

    async def _answer_question(
        self, request: str, article_link: str
    ) -> ArticleResponse:
        """
        Retrieve an article by its link and answer a question about it.
        Args:
            request: the question to answer
            article_link: the link to the article
        Returns:
            ArticleResponse: the response with the article content
        """
        article = self._get_article(article_link, use_cache=self.use_cache)
        return await self._article_agent.run(
            USER_PROMPT_ARTICLE_TEMPLATE.format(request=request, article=article)
        )

    async def run(self, request: str) -> ArticleResponse:
        """
        Run the article agent to answer a question about an article.
        Args:
            request: the question to answer
        Returns:
            ArticleResponse: the response with the article content
        """
        # Discriminate the type of article request

        article_request = await self._discriminate_article_request(request)

        logger.info(
            f"{datetime.now()}: Discriminated article request: {article_request}"
        )

        if article_request.output.article_type == "title":
            # Search for the article by title
            article_title = article_request.output.article_value
            retrieve_article = await self._retrieve_article(article_title)
            article_link = retrieve_article.output.article_link
        else:
            # If the article type is not title, we assume it's a link or an error
            article_link = article_request.output.article_value

        logger.info(f"{datetime.now()}: Article link retrieved: {article_link}")

        if "No articles found" == article_link:
            return ArticleResponse(
                response="No articles found, the requested article is probably not in ArXiv.",
                article_title="",
                article_link="",
            )

        return await self._answer_question(request=request, article_link=article_link)
