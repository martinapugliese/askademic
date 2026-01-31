from unittest.mock import MagicMock, patch

from askademic.tools import get_article, identify_latest_day


@patch("askademic.tools.requests.get")
@patch("askademic.tools.feedparser.parse")
def test_identify_latest_day(mock_feedparser_parse, mock_requests_get):
    # Mock the response from requests.get
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.content = b"mock content"
    mock_requests_get.return_value = mock_response

    # Mock the parsed feedparser response
    mock_feedparser_parse.return_value = {
        "entries": [{"published": "2025-03-29T12:00:00Z"}]
    }
    result = identify_latest_day("cs.AI")

    assert result == "2025-03-29"
    mock_requests_get.assert_called_once_with(
        "http://export.arxiv.org/api/query?search_query="
        + "cat:cs.AI&start=0&max_results=1&sortBy=submittedDate&sortOrder=descending",
        timeout=360,
    )
    mock_feedparser_parse.assert_called_once_with(b"mock content")


@patch("askademic.tools.requests.get")
def test_identify_latest_day_error(mock_requests_get):
    # Mock the response with an error status
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_requests_get.return_value = mock_response

    result = identify_latest_day("cs.AI")

    assert result == "Not Found"
    mock_requests_get.assert_called_once_with(
        "http://export.arxiv.org/api/query?search_query="
        + "cat:cs.AI&start=0&max_results=1&sortBy=submittedDate&sortOrder=descending",
        timeout=360,
    )

    @patch("askademic.tools.requests.get")
    @patch("askademic.tools.pymupdf.open")
    def test_get_article_success(mock_pymupdf_open, mock_requests_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.content = b"mock pdf content"
        mock_requests_get.return_value = mock_response

        # Mock the pymupdf.open behavior
        mock_doc = MagicMock()
        mock_doc.__enter__.return_value = mock_doc
        mock_doc.__exit__.return_value = None
        mock_doc.pages = [MagicMock(get_text=MagicMock(return_value="Page 1 content"))]
        mock_pymupdf_open.return_value = mock_doc

        result = get_article("http://example.com/mock.pdf")

        assert "Page 1 content" in result
        mock_requests_get.assert_called_once_with(
            "http://example.com/mock.pdf", timeout=360
        )
        mock_pymupdf_open.assert_called_once()


def test_get_article_():

    article = get_article("http://arxiv.org/pdf/1604.06737v1")

    assert "Unlike unstructured data found in nature," in article


def test_get_article_is_curtailed():

    # a book
    article = get_article("http://arxiv.org/pdf/1302.6946")

    assert len(article) == 70058  # max len + xml tags
    assert article.startswith("<article url=")
    assert article.endswith("</article>")
