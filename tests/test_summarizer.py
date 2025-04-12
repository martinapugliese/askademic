import asyncio
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from pydantic_ai.agent import AgentRunResult

from askademic.summarizer import Category, Summary, SummaryAgent, SummaryResponse

testdata = [
    (
        "get me the latest papers in AI",
        Category(category_id="cs.AI", category_name="Artificial Intelligence"),
        Summary(summary="Summary of cs.AI articles."),
        SummaryResponse(
            category=Category(
                category_id="cs.AI", category_name="Artificial Intelligence"
            ),
            latest_published_day="2025-03-29",
            summary=Summary(summary="Summary of cs.AI articles."),
            recent_papers_url="http://arxiv.org/cs.AI",
        ),
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("agent_request, category, summary, summary_response", testdata)
async def test_summary_agent(agent_request, category, summary, summary_response):
    """Test the SummaryAgent class."""
    summary_agent = SummaryAgent()
    summary_agent._category_agent = MagicMock()
    summary_agent._summary_agent = MagicMock()

    summary_agent._category_agent.run.return_value = AgentRunResult(
        data=category, _result_tool_name=None, _state=None, _new_message_index=None
    )
    summary_agent._summary_agent.run.return_value = AgentRunResult(
        data=summary, _result_tool_name=None, _state=None, _new_message_index=None
    )

    response = await summary_agent(agent_request)
    assert response == summary_response
