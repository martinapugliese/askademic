from pydantic import BaseModel, Field
from pydantic_ai import Agent

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts import (
    SYSTEM_PROMPT_ARTICLE,
    SYSTEM_PROMPT_ARTICLE_RETRIEVEL,
    SYSTEM_PROMPT_REQUEST_DISCRIMINATOR,
    USER_PROMPT_ARTICLE_RETRIEVEL_TEMPLATE,
    USER_PROMPT_ARTICLE_TEMPLATE,
    USER_PROMPT_REQUEST_DISCRIMINATOR_TEMPLATE,
)
from askademic.tools import get_article, search_articles_by_title


class ArticleRequestDiscriminatorResponse(BaseModel):
    article_type: str = Field(
        description="The type of article request: 'title', 'link', or 'error'."
    )
    article_value: str = Field(
        description="The article title, link or an emtpy string if the type is error."
    )


class ArticleResponse(BaseModel):
    response: str = Field(description="The response to the request")
    article_title: str = Field(
        description="The title of the article you used to answer the request."
    )
    article_link: str = Field(
        description="The article link you used to answer the request."
    )


class ArticleRetrievalResponse(BaseModel):
    article_link: str = Field(description="The article link you found.")
    article_title: str = Field(description="The title of the article you found.")


class ArticleAgent:
    def __init__(self):

        self._get_article = get_article
        self._search_articles_by_title = search_articles_by_title

        self._article_request_discriminator_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_REQUEST_DISCRIMINATOR,
            output_type=ArticleRequestDiscriminatorResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._article_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_ARTICLE,
            output_type=ArticleResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
        )

        self._article_retrieval_agent = Agent(
            GEMINI_2_FLASH_MODEL_ID,
            system_prompt=SYSTEM_PROMPT_ARTICLE_RETRIEVEL,
            output_type=ArticleRetrievalResponse,
            model_settings={"max_tokens": 1000, "temperature": 0},
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
        article = self._get_article(article_link)
        return await self._article_agent.run(
            USER_PROMPT_ARTICLE_TEMPLATE.format(request=request, article=article)
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
            USER_PROMPT_ARTICLE_RETRIEVEL_TEMPLATE.format(
                article_title=article_title, articles=articles
            )
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

        if article_request.output.article_type == "title":
            # Search for the article by title
            article_title = article_request.output.article_value
            retrieve_article = await self._retrieve_article(article_title)
            article_link = retrieve_article.output.article_link
        else:
            # If the article type is not title, we assume it's a link or an error
            article_link = article_request.output.article_value

        return await self._answer_question(request=request, article_link=article_link)


article_agent = ArticleAgent()
