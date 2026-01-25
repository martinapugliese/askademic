import asyncio
import os
from unittest.mock import MagicMock

import pytest
from pydantic_ai.agent import AgentRunResult

os.environ["GOOGLE_API_KEY"] = "mock"

from askademic.question import (  # noqa: E402
    QuestionAgent,
    QuestionAnswerResponse,
)


@pytest.fixture
def question_agent():
    """Create a QuestionAgent instance for testing."""
    return QuestionAgent("google-gla:gemini-2.0-flash")


def test_question_agent_initialization(question_agent):
    """Test that QuestionAgent initializes correctly."""
    assert question_agent._agent is not None
    assert question_agent.use_cache is True


def test_question_agent_initialization_no_cache():
    """Test QuestionAgent initialization with cache disabled."""
    agent = QuestionAgent("google-gla:gemini-2.0-flash", use_cache=False)
    assert agent.use_cache is False


@pytest.mark.parametrize(
    "link,expected",
    [
        (
            "https://arxiv.org/pdf/1706.03762.pdf",
            "https://arxiv.org/pdf/1706.03762.pdf",
        ),
        (
            "https://arxiv.org/abs/1706.03762",
            "https://arxiv.org/pdf/1706.03762.pdf",
        ),
        (
            "1706.03762",
            "https://arxiv.org/pdf/1706.03762.pdf",
        ),
        (
            "2401.00001",
            "https://arxiv.org/pdf/2401.00001.pdf",
        ),
        (
            "invalid_link",
            "invalid_link",
        ),
    ],
)
def test_normalize_arxiv_link(question_agent, link, expected):
    """Test that arXiv links are normalized correctly."""
    result = question_agent._normalize_arxiv_link(link)
    assert result == expected


@pytest.mark.asyncio
async def test_question_agent_run():
    """Test the QuestionAgent run method with mocked agent."""
    question_agent = QuestionAgent("google-gla:gemini-2.0-flash")

    expected_response = QuestionAnswerResponse(
        response="Reinforcement learning is a type of machine learning...",
        article_list=[
            "https://arxiv.org/pdf/1706.03762.pdf",
        ],
    )

    future = asyncio.Future()
    future.set_result(
        AgentRunResult(
            output=expected_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )

    question_agent._agent = MagicMock()
    question_agent._agent.run.return_value = future

    result = await question_agent.run("what is reinforcement learning?")

    assert result.output == expected_response
    question_agent._agent.run.assert_called_once()


@pytest.mark.asyncio
async def test_question_agent_call_alias():
    """Test that __call__ is an alias for run()."""
    question_agent = QuestionAgent("google-gla:gemini-2.0-flash")

    expected_response = QuestionAnswerResponse(
        response="Test response",
        article_list=["https://arxiv.org/pdf/1234.56789.pdf"],
    )

    future = asyncio.Future()
    future.set_result(
        AgentRunResult(
            output=expected_response,
            _output_tool_name=None,
            _state=None,
            _new_message_index=None,
            _traceparent_value=None,
        )
    )

    question_agent._agent = MagicMock()
    question_agent._agent.run.return_value = future

    result = await question_agent("test question")

    assert result.output == expected_response
    question_agent._agent.run.assert_called_once()


def test_search_articles_tool():
    """Test that the search_articles tool is properly registered."""
    question_agent = QuestionAgent("google-gla:gemini-2.0-flash")

    # Check that the agent has tools registered
    assert question_agent._agent._function_toolset is not None
    tool_names = list(question_agent._agent._function_toolset.tools)
    assert "search_articles" in tool_names


def test_fetch_article_tool():
    """Test that the fetch_article tool is properly registered."""
    question_agent = QuestionAgent("google-gla:gemini-2.0-flash")

    # Check that the agent has tools registered
    assert question_agent._agent._function_toolset is not None
    tool_names = list(question_agent._agent._function_toolset.tools)
    assert "fetch_article" in tool_names
