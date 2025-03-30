from unittest.mock import MagicMock, patch

import pytest

from arxiv_muse.utils import get_arxiv_categories


@patch("arxiv_muse.utils.requests.get")
def test_get_arxiv_categories_200(mock_requests_get):

    # Sample HTML response mimicking the arXiv category taxonomy page
    sample_html = """
    <div id="category_taxonomy_list">
        <h4>cs.AI (Artificial Intelligence)</h4>
        <h4>math.OC (Optimization and Control)</h4>
        <h4>physics.optics (Optics)</h4>
    </div>
    """

    # Mock the response object
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = sample_html
    mock_requests_get.return_value = mock_response

    result = get_arxiv_categories()
    expected_result = {
        "Artificial Intelligence": "cs.AI",
        "Optimization and Control": "math.OC",
        "Optics": "physics.optics",
    }

    assert result == expected_result
    mock_requests_get.assert_called_once_with("https://arxiv.org/category_taxonomy")


@patch("arxiv_muse.utils.requests.get")
def test_get_arxiv_categories_non_200(mock_requests_get):
    # Mock the response object with a non-200 status code
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_requests_get.return_value = mock_response

    # Verify that the function raises an exception
    with pytest.raises(Exception, match="Failed to fetch page, status code: 404"):
        get_arxiv_categories()

    mock_requests_get.assert_called_once_with("https://arxiv.org/category_taxonomy")
