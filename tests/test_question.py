import asyncio
import os
from unittest.mock import MagicMock

import pytest
from pydantic_ai.agent import AgentRunResult  # noqa: F401

os.environ["GOOGLE_API_KEY"] = "mock"

from askademic.question import (  # noqa: E402
    Article,
    ArticleListResponse,
    QueryResponse,
    QuestionAgent,
    QuestionAnswerResponse,
)

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
    ),
    (
        "what is supervised learning?",
        QueryResponse(queries=["supervised learning", "machine learning"]),
        "abstracts table",
        ArticleListResponse(
            article_list=[
                Article(
                    article_url="article4_link",
                    relevance_score=0.1,
                ),
                Article(
                    article_url="article5_link",
                    relevance_score=0.1,
                ),
                Article(
                    article_url="article6_link",
                    relevance_score=0.2,
                ),
            ]
        ),
        "article_text",
        QuestionAnswerResponse(
            response="Supervised learning is a type of machine learning...",
            article_list=[
                "article4_link",
                "article5_link",
            ],
        ),
    ),
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

    assert os.environ["GOOGLE_API_KEY"] == "mock"

    question_agent = QuestionAgent("google-gla:gemini-2.0-flash")
    question_agent._query_agent = MagicMock()
    question_agent._abstract_relevance_agent = MagicMock()
    question_agent._many_articles_agent = MagicMock()
    question_agent._get_article = MagicMock()
    question_agent._search_articles_by_abs = MagicMock()

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

    question_agent._search_articles_by_abs.return_value = (
        search_articles_by_abs_response
    )

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

    question_agent._get_article.return_value = get_article_response

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

    assert response.output == question_answer_response
    assert question_agent._query_agent.run.call_count == 1

    query_list_dimension = min(
        len(query_list.queries), question_agent._query_list_limit
    )
    assert question_agent._search_articles_by_abs.call_count == query_list_dimension
    assert (
        question_agent._abstract_relevance_agent.run.call_count == query_list_dimension
    )

    article_link_list = []
    for _ in range(query_list_dimension):
        article_link_list += article_list_response.article_list
    article_link_list = [
        article.article_url
        for article in article_link_list
        if article.relevance_score >= question_agent._relevance_score_threshold
    ]
    article_link_list = article_link_list[: question_agent._article_list_limit]
    assert question_agent._get_article.call_count == len(article_link_list)

    assert question_agent._many_articles_agent.run.call_count == 1
