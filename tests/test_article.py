import asyncio
import os
from unittest.mock import MagicMock

import pytest
import pytest_asyncio  # noqa: F401
from pydantic_ai.agent import AgentRunResult  # noqa: F401

os.environ["GEMINI_API_KEY"] = "mock"

from askademic.article import (  # noqa: E402
    USER_PROMPT_ARTICLE_RETRIEVEL_TEMPLATE,
    USER_PROMPT_ARTICLE_TEMPLATE,
    USER_PROMPT_REQUEST_DISCRIMINATOR_TEMPLATE,
    ArticleAgent,
    ArticleRequestDiscriminatorResponse,
    ArticleResponse,
    ArticleRetrievalResponse,
)

testdata = [
    (
        "what the 'Augmented Synthetic Control' paper about?",
        ArticleRequestDiscriminatorResponse(
            article_type="title", article_value="Augmented Synthetic Control"
        ),
        ArticleRetrievalResponse(
            article_link="https://arxiv.org/abs/2401.00001",
            article_title="Augmented Synthetic Control",
        ),
        ArticleResponse(
            response="The 'Augmented Synthetic Control' paper discusses...",
            article_title="Augmented Synthetic Control",
            article_link="https://arxiv.org/abs/2401.00001",
        ),
    ),
    (
        "what is the paper with id 2401.00001 about?",
        ArticleRequestDiscriminatorResponse(
            article_type="link", article_value="https://arxiv.org/abs/2401.00001"
        ),
        ArticleRetrievalResponse(
            article_link="https://arxiv.org/abs/2401.00001",
            article_title="Augmented Synthetic Control",
        ),
        ArticleResponse(
            response="The paper with id 2401.00001 discusses...",
            article_title="Augmented Synthetic Control",
            article_link="https://arxiv.org/abs/2401.00001",
        ),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question, request_discriminator_response, retrieval_response, expected_response",
    testdata,
)
async def test_article_agent(
    question: str,
    request_discriminator_response: ArticleRequestDiscriminatorResponse,
    retrieval_response: ArticleRetrievalResponse,
    expected_response: ArticleResponse,
):

    # Mock the agents
    article_agent = ArticleAgent(
        model="gemini-2.0-flash",
    )
    article_agent._get_article = MagicMock(
        return_value="Mocked article text for testing purposes."
    )
    article_agent._search_articles_by_title = MagicMock(
        return_value="Mocked search articles by title response."
    )

    request_discriminator_response_future = asyncio.Future()
    request_discriminator_response_future.set_result(
        AgentRunResult(
            output=request_discriminator_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    article_agent._article_request_discriminator_agent = MagicMock(
        run=MagicMock(return_value=request_discriminator_response_future)
    )

    retrieval_response_future = asyncio.Future()
    retrieval_response_future.set_result(
        AgentRunResult(
            output=retrieval_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    article_agent._article_retrieval_agent = MagicMock(
        run=MagicMock(return_value=retrieval_response_future)
    )

    expected_response_future = asyncio.Future()
    expected_response_future.set_result(
        AgentRunResult(
            output=expected_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    article_agent._article_agent = MagicMock(
        run=MagicMock(return_value=expected_response_future)
    )

    # Run the agent
    response = await article_agent.run(question)
    assert response.output == expected_response

    article_agent._article_request_discriminator_agent.run.assert_called_once_with(
        USER_PROMPT_REQUEST_DISCRIMINATOR_TEMPLATE.format(request=question)
    )

    # Check if the article retrieval agent was called correctly
    if request_discriminator_response.article_type == "title":
        article_agent._search_articles_by_title.assert_called_once_with(
            request_discriminator_response.article_value
        )
        article_agent._article_retrieval_agent.run.assert_called_once_with(
            USER_PROMPT_ARTICLE_RETRIEVEL_TEMPLATE.format(
                article_title=request_discriminator_response.article_value,
                articles="Mocked search articles by title response.",
            )
        )
        article_agent._get_article.assert_called_once_with(
            retrieval_response.article_link
        )

    else:
        article_agent._get_article.assert_called_once_with(
            request_discriminator_response.article_value
        )

    article_agent._article_agent.run.assert_called_once_with(
        USER_PROMPT_ARTICLE_TEMPLATE.format(
            request=question, article="Mocked article text for testing purposes."
        )
    )
