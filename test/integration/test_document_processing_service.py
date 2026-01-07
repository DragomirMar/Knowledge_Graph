import pytest
import logging
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from services.document_processing_service import process_documents
from database.database_manager import DBManager as dbm

logger = logging.getLogger(__name__)


@pytest.fixture
def cleanup_db():
    """Clean database after tests"""
    yield
    dbm.drop_collection_entities()
    dbm.drop_collection_relationships()


@patch('services.document_processing_service.extract_from_pdf')
@patch('services.document_processing_service.OllamaModel')
def test_process_pdf_documents(mock_llm_class, mock_extract_pdf, cleanup_db):
    """Test processing PDF documents"""
    # Setup mocks
    mock_chunk = Mock()
    mock_chunk.page_content = "Test content about Liverpool FC."
    mock_extract_pdf.return_value = [mock_chunk]
    
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    # Mock entity extraction
    with patch('services.document_processing_service.em.extract_entities_and_relationships_from_chunks') as mock_extract:
        mock_extract.return_value = {
            "entities": {
                "Liverpool Fc": "A football club"
            },
            "relationships": [
                ("Liverpool Fc", "plays in", "Premier League")
            ]
        }
        
        # Create mock PDF file
        mock_pdf = Mock()
        mock_pdf.read.return_value = b"fake pdf content"
        mock_pdf.name = "test.pdf"
        
        # Process
        entity_count, rel_count = process_documents([mock_pdf], [])
        
        # Verify
        assert entity_count == 1
        assert rel_count == 1
        
        # Verify stored in database
        entities = dbm.get_all_entities()
        assert len(entities) >= 1


@patch('services.document_processing_service.extract_from_url')
@patch('services.document_processing_service.OllamaModel')
def test_process_url_documents(mock_llm_class, mock_extract_url, cleanup_db):
    """Test processing URL documents"""
    # Setup mocks
    mock_chunk = Mock()
    mock_chunk.page_content = "Test content from URL."
    mock_extract_url.return_value = [mock_chunk]
    
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    # Mock entity extraction
    with patch('services.document_processing_service.em.extract_entities_and_relationships_from_chunks') as mock_extract:
        mock_extract.return_value = {
            "entities": {
                "Test Entity": "A test entity"
            },
            "relationships": []
        }
        
        # Process
        entity_count, rel_count = process_documents([], ["http://example.com"])
        
        # Verify
        assert entity_count == 1
        assert rel_count == 0


@patch('services.document_processing_service.extract_from_pdf')
def test_process_handles_pdf_extraction_errors(mock_extract_pdf, cleanup_db):
    """Test that PDF extraction errors are handled gracefully"""
    mock_extract_pdf.side_effect = Exception("PDF extraction failed")
    
    mock_pdf = Mock()
    mock_pdf.read.return_value = b"fake pdf"
    mock_pdf.name = "bad.pdf"
    
    # Should not raise exception
    entity_count, rel_count = process_documents([mock_pdf], [])
    
    # Should return 0 since extraction failed
    assert entity_count == 0
    assert rel_count == 0


@patch('services.document_processing_service.extract_from_pdf')
@patch('services.document_processing_service.OllamaModel')
def test_process_handles_entity_creation_errors(mock_llm_class, mock_extract_pdf, cleanup_db):
    """Test handling of entity creation errors"""
    mock_chunk = Mock()
    mock_chunk.page_content = "Content"
    mock_extract_pdf.return_value = [mock_chunk]
    
    mock_llm = Mock()
    mock_llm_class.return_value = mock_llm
    
    with patch('services.document_processing_service.em.extract_entities_and_relationships_from_chunks') as mock_extract:
        mock_extract.return_value = {
            "entities": {
                "Entity1": "Description1",
                "Entity2": "Description2"
            },
            "relationships": []
        }
        
        # Make one entity creation fail
        with patch('services.document_processing_service.dbm.create_entity') as mock_create:
            mock_create.side_effect = [None, Exception("Creation failed")]
            
            mock_pdf = Mock()
            mock_pdf.read.return_value = b"fake pdf"
            mock_pdf.name = "test.pdf"
            
            # Should handle error gracefully
            entity_count, rel_count = process_documents([mock_pdf], [])
            
            # Should still count the successful one
            assert entity_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])