import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from askademic.tools import (
    get_article,
    get_article_from_cache,
    get_cache_key,
    get_cache_path,
    save_article_to_cache,
)


class TestArticleCache:
    @pytest.fixture
    def temp_cache_dir(self):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Patch the get_cache_path function to return our temp directory
        with patch("askademic.tools.get_cache_path", return_value=Path(temp_dir)):
            yield temp_dir
            
        # Clean up after test
        shutil.rmtree(temp_dir)
    
    def test_get_cache_key(self):
        # Test that the same URL always generates the same key
        url = "https://arxiv.org/pdf/2401.00001.pdf"
        key1 = get_cache_key(url)
        key2 = get_cache_key(url)
        assert key1 == key2
        
        # Test that different URLs generate different keys
        url2 = "https://arxiv.org/pdf/2401.00002.pdf"
        key3 = get_cache_key(url2)
        assert key1 != key3
    
    def test_save_and_retrieve_from_cache(self, temp_cache_dir):
        url = "https://arxiv.org/pdf/2401.00001.pdf"
        content = "Test article content"
        
        # Save to cache
        save_article_to_cache(url, content)
        
        # Verify file exists in temp directory
        cache_file = Path(temp_cache_dir) / f"{get_cache_key(url)}.json"
        assert cache_file.exists()
        
        # Retrieve from cache
        hit, retrieved_content = get_article_from_cache(url)
        assert hit is True
        assert retrieved_content == content
    
    def test_cache_miss(self, temp_cache_dir):
        url = "https://arxiv.org/pdf/nonexistent.pdf"
        
        # Try to retrieve non-existent article
        hit, content = get_article_from_cache(url)
        assert hit is False
        assert content == ""
    
    def test_article_retrieval_with_cache(self, temp_cache_dir):
        url = "https://arxiv.org/pdf/2401.00001.pdf"
        test_content = "Test article content"
        formatted_content = f"""
        -------{url}------------
        {test_content}
        ------END----------------
    """
        
        # Directly save content to cache first
        save_article_to_cache(url, formatted_content)
        
        # First call should use cache
        with patch("askademic.tools.requests.get") as mock_get:
            result1 = get_article(url, use_cache=True)
            assert not mock_get.called  # Should not make a network call
            assert result1 == formatted_content
            
        # Call with cache disabled - should try to use network
        with patch("askademic.tools.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.content = b"Test content"
            mock_get.return_value = mock_response
            
            with patch("askademic.tools.pymupdf.open") as mock_open:
                mock_doc = MagicMock()
                mock_page = MagicMock()
                mock_page.get_text.return_value = "New test content"
                mock_doc.__enter__.return_value = [mock_page]
                mock_open.return_value = mock_doc
                
                result2 = get_article(url, use_cache=False)
                assert mock_get.called  # Should make a network call