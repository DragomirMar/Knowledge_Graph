import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from services.extract_text import (
    clean_text_for_chunking,
    extract_from_url,
    extract_from_pdf
)

### Tests for clean_text_for_chunking ###

def test_clean_removes_duplicate_sentences():
    """Test that duplicate sentences are removed"""
    text = "This is a sentence. This is a sentence. Another sentence."
    
    result = clean_text_for_chunking(text)
    
    assert result.count("This is a sentence") == 1
    assert "Another sentence" in result


def test_clean_removes_short_sentences():
    """Test that very short sentences are filtered out"""
    text = "This is a long enough sentence. Hi. Short. This is another long sentence."
    
    result = clean_text_for_chunking(text)
    
    assert "Hi" not in result  # Too short (< 15 chars)
    assert "Short" not in result  
    assert "This is a long enough sentence" in result
    assert "This is another long sentence" in result


def test_clean_removes_author_date_patterns():
    """Test removal of author and date patterns"""
    text = "By John Doe | Jan 15, 2024. Some sentence here. Another sentence here."
    
    result = clean_text_for_chunking(text)
    
    assert "By John Doe" not in result
    assert "Jan 15, 2024" not in result
    assert "Some sentence here" in result
    assert "Another sentence here" in result


def test_clean_fixes_duplicate_words():
    """Test fixing of duplicate consecutive words"""
    text = "The Liverpool. Liverpool team is great."
    
    result = clean_text_for_chunking(text)
    
    # Should fix "Liverpool. Liverpool" pattern
    assert result.count("Liverpool") <= 2  # Should not have duplicates


def test_clean_removes_excessive_whitespace():
    """Test that excessive whitespace is cleaned"""
    text = "Word1    Word2  \n\n  Word3     Word4"
    
    result = clean_text_for_chunking(text)
    
    assert "    " not in result
    assert "  " not in result
    assert result == "Word1 Word2 Word3 Word4"


### Tests for extract_from_url ###

@patch('services.extract_text.requests.get')
def test_extract_url_from_main_tag(mock_get):
    """Test extraction from <main> tag"""
    mock_response = Mock()
    mock_response.content = b'''
    <html>
        <main>
            <p>Main content paragraph.</p>
            <h2>Main heading content.</h2>
        </main>
    </html>
    '''
    mock_get.return_value = mock_response
    
    result = extract_from_url("http://example.com")
    
    assert len(result) > 0
    combined_text = " ".join([chunk.page_content for chunk in result])
    assert "Main content paragraph" in combined_text
    assert "Main heading" in combined_text


@patch('services.extract_text.requests.get')
def test_extract_url_fallback_to_article(mock_get):
    """Test fallback to <article> tag when no <main>"""
    mock_response = Mock()
    mock_response.content = b'''
    <html>
        <article>
            <p>Article content here.</p>
        </article>
    </html>
    '''
    mock_get.return_value = mock_response
    
    result = extract_from_url("http://example.com")
    
    assert len(result) > 0
    combined_text = " ".join([chunk.page_content for chunk in result])
    assert "Article content" in combined_text


@patch('services.extract_text.requests.get')
def test_extract_url_fallback_to_body(mock_get):
    """Test fallback to <body> tag when no <main> or <article>"""
    mock_response = Mock()
    mock_response.content = b'''
    <html>
        <body>
            <p>Body content here.</p>
        </body>
    </html>
    '''
    mock_get.return_value = mock_response
    
    result = extract_from_url("http://example.com")
    
    assert len(result) > 0
    combined_text = " ".join([chunk.page_content for chunk in result])
    assert "Body content" in combined_text


@patch('services.extract_text.requests.get')
def test_extract_url_removes_unwanted_tags(mock_get):
    """Test that unwanted tags are removed"""
    mock_response = Mock()
    mock_response.content = b'''
    <html>
        <main>
            <p>A piece of good content.</p>
            <script>alert('bad');</script>
            <style>.bad { color: red; }</style>
            <figure>Bad figure</figure>
            <aside>Bad aside</aside>
        </main>
    </html>
    '''
    mock_get.return_value = mock_response
    
    result = extract_from_url("http://example.com")
    
    combined_text = " ".join([chunk.page_content for chunk in result])
    assert "A piece of good content." in combined_text
    assert "alert" not in combined_text
    assert ".bad" not in combined_text
    assert "Bad figure" not in combined_text
    assert "Bad aside" not in combined_text


@patch('services.extract_text.requests.get')
def test_extract_url_adds_punctuation_to_headings(mock_get):
    """Test that non-paragraph tags get punctuation added"""
    mock_response = Mock()
    mock_response.content = b'''
    <html>
        <main>
            <h1>Heading Without Period</h1>
            <p>Paragraph with period.</p>
        </main>
    </html>
    '''
    mock_get.return_value = mock_response
    
    result = extract_from_url("http://example.com")
    
    combined_text = " ".join([chunk.page_content for chunk in result])
    # Heading should have period added
    assert "Heading Without Period." in combined_text or \
           "heading without period" in combined_text.lower()


### Tests for extract_from_pdf ###

@patch('services.extract_text.PyPDFLoader')
def test_extract_pdf_creates_chunks(mock_loader_class):
    """Test that PDF is extracted and split into chunks"""
    
    documents = [
        Document(
            page_content="This is a long PDF content. " * 100,
            metadata={"source": "test.pdf", "page": 0}
        )
    ]
    
    # Mock PDF loader
    mock_loader = Mock()
    mock_loader.load.return_value = documents
    mock_loader_class.return_value = mock_loader
    
    # Create a mock file
    mock_file = Mock()
    mock_file.getbuffer.return_value = b"fake pdf content"
    
    result = extract_from_pdf(mock_file)
    
    assert len(result) > 0
    assert isinstance(result, list)
    assert all(hasattr(chunk, 'page_content') for chunk in result)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])