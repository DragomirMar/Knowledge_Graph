import pytest
import logging
from unittest.mock import Mock
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from entity_manager import (
    merge_entity_descriptions,
    clean_and_validate_relationships,
    extract_entities_and_relationships_from_chunks
)

logger = logging.getLogger(__name__)

### Tests for merge_entity_descriptions ###

def test_merge_removes_duplicates():
    """Test that duplicate sentences are removed"""
    descriptions = [
        "Liverpool is a football club.",
        "Liverpool is a football club.",
        "They play in England."
    ]
    
    result = merge_entity_descriptions(descriptions)
    
    assert result == "Liverpool is a football club. They play in England."
    assert result.count("Liverpool is a football club") == 1


def test_merge_filters_short_fragments():
    """Test that very short fragments are ignored"""
    descriptions = [
        "Liverpool FC is a professional football club.",
        "Yes",  # Too short (< 10 chars)
        "They compete in the Premier League."
    ]
    
    result = merge_entity_descriptions(descriptions)
    
    assert "Yes" not in result
    assert "Liverpool FC" in result
    assert "Premier League" in result


def test_merge_case_insensitive_duplicate_detection():
    """Test that duplicates are detected case-insensitively"""
    descriptions = [
        "Liverpool is a club.",
        "Liverpool is a club.",  # Same case
        "liverpool is a club."   # Different case
    ]
    
    result = merge_entity_descriptions(descriptions)
    
    assert result.count("Liverpool is a club") == 1


### Tests for clean_and_validate_relationships ###

def test_clean_filters_malformed_relationships():
    """Test that malformed relationships are filtered out"""
    relationships = [
        ("Entity1", "relates to", "Entity2"),  # Valid
        None,  # Invalid
        ("Entity5",),  # Invalid 
        ("Entity6", "predicate", "Entity7", "extra"),  # Invalid
        ("", "predicate", "Entity8"),  # Invalid 
        ("Entity9", "predicate", ""),  # Invalid 
        (None, "predicate", "Entity1"), # Invalid 
        ("Entity4", "predicate", None), # Invalid 
    ]
    
    result = clean_and_validate_relationships(relationships)
    
    assert len(result) == 1
    assert result[0] == ("Entity1", "relates to", "Entity2")


def test_clean_removes_duplicate_relationships():
    """Test that duplicate relationships are removed"""
    relationships = [
        ("Entity1", "relates to", "Entity2"),
        ("Entity1", "relates to", "Entity2"),  # Exact duplicate
        ("Entity3", "connects", "Entity4"),
        ("Entity3", "connects", "Entity4"),  # Another duplicate
    ]
    
    result = clean_and_validate_relationships(relationships)
    
    assert len(result) == 2
    # Each relationship should appear only once
    rel_set = set(result)
    assert len(rel_set) == len(result)


def test_clean_strips_whitespace_from_elements():
    """Test that whitespace is stripped from relationship elements"""
    relationships = [
        ("  Entity1  ", "  relates to  ", "  Entity2  "),
    ]
    
    result = clean_and_validate_relationships(relationships)
    
    assert len(result) == 1
    subject, predicate, obj = result[0]
    assert subject == "Entity1"
    assert predicate == "relates to"
    assert obj == "Entity2"


### Tests for extract_entities_and_relationships_from_chunks ###

@pytest.fixture
def mock_llm():
    """Create a mock LLM"""
    return Mock()


@pytest.fixture
def sample_chunks():
    """Create sample document chunks"""
    chunk1 = Mock()
    chunk1.page_content = "Liverpool FC is a football club. Trent Alexander-Arnold plays for Liverpool."
    
    chunk2 = Mock()
    chunk2.page_content = "Liverpool FC competes in the Premier League."
    
    return [chunk1, chunk2]


def test_extraction_combines_duplicate_entities(mock_llm, sample_chunks):
    """Test that entities with same name get descriptions merged"""
    
    mock_llm.extract_knowledge_simultaneously.side_effect = [
        {
            "entities": {
                "Liverpool Fc": "A football club.",
                "Trent Alexander-Arnold": "A player."
            },
            "relationships": [("Liverpool Fc", "has", "Trent Alexander-Arnold")]
        },
        {
            "entities": {
                "Liverpool Fc": "Competes in Premier League.", 
            },
            "relationships": [("Liverpool Fc", "plays in", "Premier League")]
        }
    ]
    
    result = extract_entities_and_relationships_from_chunks(
        sample_chunks, mock_llm, max_chunks=2
    )
    
    entities = result["entities"]
    
    # Liverpool FC should appear once with merged description
    assert "Liverpool Fc" in entities
    description = entities["Liverpool Fc"]
    
    # Both descriptions should be in the merged result
    assert "football club" in description.lower()
    assert "premier league" in description.lower()


def test_extraction_removes_duplicate_relationships(mock_llm, sample_chunks):
    """Test that duplicate relationships are removed"""
    mock_llm.extract_knowledge_simultaneously.side_effect = [
        {
            "entities": {"Liverpool Fc": "A club."},
            "relationships": [
                ("Liverpool Fc", "has", "Player"),
                ("Liverpool Fc", "has", "Player"), 
            ]
        }
    ]
    
    result = extract_entities_and_relationships_from_chunks(
        sample_chunks[:1], mock_llm, max_chunks=1
    )
    
    relationships = result["relationships"]
    
    assert len(relationships) == 1
    assert relationships[0] == ("Liverpool Fc", "has", "Player")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])