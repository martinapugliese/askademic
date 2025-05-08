import asyncio
from unittest.mock import MagicMock

import pytest
import pytest_asyncio  # noqa: F401
from pydantic_ai.agent import AgentRunResult  # noqa: F401

from askademic.question import (
    Article,
    ArticleListResponse,
    QueryResponse,
    QuestionAgent,
    QuestionAnswerResponse,
)


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "mocked_gemini_api_key")


testdata = [
    (
        "what is reinforcement learning?",
        QueryResponse(queries=["reinforcement learning"]),
        "abstracts table",
        ArticleListResponse(
            article_list=[
                Article(
                    article_url="article1_link",
                    relevance_score=0.9,
                ),
                Article(
                    article_url="article2_link",
                    relevance_score=0.8,
                ),
                Article(
                    article_url="article3_link",
                    relevance_score=0.1,
                ),
            ]
        ),
        "article_text",
        QuestionAnswerResponse(
            response="Reinforcement learning is a type of machine learning...",
            article_list=[
                "article1_link",
                "article2_link",
            ],
        ),
    )
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question, query_list, search_articles_by_abs_response, "
    "article_list_response, get_article_response, question_answer_response",
    testdata,
)
async def test_question_agent(
    question,
    query_list,
    search_articles_by_abs_response,
    article_list_response,
    get_article_response,
    question_answer_response,
):
    """Test the QuestionAgent class."""
    question_agent = QuestionAgent()
    question_agent._search_articles_by_abs = MagicMock(
        return_value=search_articles_by_abs_response
    )
    question_agent._get_article = MagicMock(return_value=get_article_response)
    question_agent._query_agent = MagicMock()
    question_agent._abstract_relevance_agent = MagicMock()
    question_agent._many_articles_agent = MagicMock()

    query_list_future = asyncio.Future()
    query_list_future.set_result(
        AgentRunResult(
            output=query_list,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    question_agent._query_agent.run.return_value = query_list_future

    article_list_future = asyncio.Future()
    article_list_future.set_result(
        AgentRunResult(
            output=article_list_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    question_agent._abstract_relevance_agent.run.return_value = article_list_future

    question_answer_future = asyncio.Future()
    question_answer_future.set_result(
        AgentRunResult(
            output=question_answer_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )
    question_agent._many_articles_agent.run.return_value = question_answer_future

    response = await question_agent(question=question)
    assert response == question_answer_response
