import os

import pytest

os.environ["GOOGLE_API_KEY"] = "mock"

from askademic.article import ArticleAgent, ArticleResponse  # noqa: E402


class TestArticleAgent:
    """Tests for the refactored ArticleAgent with tools."""

    def test_normalize_arxiv_link_pdf_url(self):
        """Test that PDF URLs are returned as-is."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        url = "https://arxiv.org/pdf/1706.03762.pdf"
        assert agent._normalize_arxiv_link(url) == url

    def test_normalize_arxiv_link_abs_url(self):
        """Test that abstract URLs are converted to PDF URLs."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        url = "https://arxiv.org/abs/1706.03762"
        expected = "https://arxiv.org/pdf/1706.03762.pdf"
        assert agent._normalize_arxiv_link(url) == expected

    def test_normalize_arxiv_link_id_only(self):
        """Test that bare arXiv IDs are converted to PDF URLs."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        arxiv_id = "1706.03762"
        expected = "https://arxiv.org/pdf/1706.03762.pdf"
        assert agent._normalize_arxiv_link(arxiv_id) == expected

    def test_normalize_arxiv_link_new_format_id(self):
        """Test that new format arXiv IDs (5 digits) are handled."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        arxiv_id = "2401.00001"
        expected = "https://arxiv.org/pdf/2401.00001.pdf"
        assert agent._normalize_arxiv_link(arxiv_id) == expected

    def test_normalize_arxiv_link_invalid(self):
        """Test that invalid links are returned as-is."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        invalid = "not-a-valid-link"
        assert agent._normalize_arxiv_link(invalid) == invalid

    def test_agent_has_tools(self):
        """Test that the agent is configured with the expected tools."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")
        tool_names = list(agent._agent._function_toolset.tools.keys())
        assert "search_by_title" in tool_names
        assert "fetch_article" in tool_names

    @pytest.mark.asyncio
    async def test_run_with_mocked_agent(self):
        """Test the run method with a mocked internal agent."""
        from unittest.mock import AsyncMock, MagicMock

        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")

        mock_response = ArticleResponse(
            response="This paper discusses attention mechanisms.",
            article_title="Attention Is All You Need",
            article_link="https://arxiv.org/pdf/1706.03762.pdf",
        )

        mock_result = MagicMock()
        mock_result.output = mock_response

        agent._agent.run = AsyncMock(return_value=mock_result)

        result = await agent.run("What is the Attention paper about?")

        assert result.output == mock_response
        agent._agent.run.assert_called_once()


class TestArticleAgentIntegration:
    """Integration-style tests that mock the external tools."""

    @pytest.mark.asyncio
    async def test_search_by_title_tool_schema(self):
        """Test that search_by_title tool has the expected schema."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")

        tools = agent._agent._function_toolset.tools
        assert "search_by_title" in tools

        # Verify the tool has the expected parameter via its function schema
        search_tool = tools["search_by_title"]
        json_schema = search_tool.function_schema.json_schema
        assert "title" in json_schema.get("properties", {})

    @pytest.mark.asyncio
    async def test_fetch_article_tool_schema(self):
        """Test that fetch_article tool has the expected schema."""
        agent = ArticleAgent(model="google-gla:gemini-2.0-flash")

        tools = agent._agent._function_toolset.tools
        assert "fetch_article" in tools

        # Verify the tool has the expected parameter via its function schema
        fetch_tool = tools["fetch_article"]
        json_schema = fetch_tool.function_schema.json_schema
        assert "link" in json_schema.get("properties", {})
