import pytest
import logging
import sys
import os
from io import BytesIO
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from services.extract_text import extract_from_url, extract_from_pdf
from llm import OllamaModel
from configuration.logger_config import setup_logging
import entity_manager as em
from database.database_manager import DBManager as dbm

setup_logging()
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def cleanup_db():
    """Clean database before and after tests"""
    yield
    # Cleanup after all tests in this module
    dbm.drop_collection_entities()
    dbm.drop_collection_relationships()


@pytest.mark.integration
@pytest.mark.slow
def test_url_extraction_and_storage_workflow(cleanup_db):
    """Test complete workflow: URL -> chunks -> entities -> database"""
    logger.info('========== Testing URL Workflow ==========')
    
    url = 'https://www.90min.com/why-liverpool-could-still-receive-trent-alexander-arnold-transfer-fee'
    
    # 1. Extract chunks
    logger.info("*********** Extract chunks from URL ***********")
    chunks_url = extract_from_url(url)
    assert len(chunks_url) > 0, "Should extract at least one chunk"
    logger.info(f"✓ Extracted {len(chunks_url)} chunks")

    # 2. Extract entities and relationships
    logger.info("*********** Extract entities and relationships ***********")
    llm = OllamaModel()
    final_entities = em.extract_entities_and_relationships_from_chunks(
        chunks_url, llm, max_chunks=2  # Limited for testing
    )
    
    entities = final_entities["entities"]
    relationships = final_entities["relationships"]
    
    assert len(entities) > 0, "Should extract at least one entity"
    logger.info(f"✓ Extracted {len(entities)} entities")
    logger.info(f"✓ Extracted {len(relationships)} relationships")

    # 3. Store in database
    logger.info("*********** Store entities in database ***********")
    entity_count = 0
    for name, description in entities.items():
        try:
            dbm.create_entity(name, description)
            entity_count += 1
            logger.info(f"✓ Stored entity: {name}")
        except Exception as e:
            logger.warning(f"Could not store entity {name}: {e}")
    
    relationship_count = 0
    for subject, predicate, obj in relationships:
        try:
            dbm.create_relationship(subject, predicate, obj)
            relationship_count += 1
            logger.info(f"✓ Stored relationship: {subject} -> {predicate} -> {obj}")
        except Exception as e:
            logger.warning(f"Could not store relationship: {e}")
    
    # Verify storage
    stored_entities = dbm.get_entity_count()
    stored_relationships = dbm.get_relationship_count()
    
    assert stored_entities >= entity_count, "Entities should be stored"
    assert stored_relationships >= relationship_count, "Relationships should be stored"
    
    logger.info(f"✓ Final counts: {stored_entities} entities, {stored_relationships} relationships")


@pytest.mark.integration
@pytest.mark.slow
def test_pdf_extraction_and_storage_workflow(cleanup_db):
    """Test complete workflow: PDF -> chunks -> entities -> database"""
    logger.info('========== Testing PDF Workflow ==========')
    
    # Path to test PDF file
    test_dir = Path(__file__).parent.parent  # Goes to test/
    pdf_file_path = test_dir / 'data' / 'Formula.pdf'
    
    # 1. Load PDF file
    logger.info("*********** Loading PDF file ***********")
    with open(pdf_file_path, 'rb') as f:
        file_like = BytesIO(f.read())
    logger.info(f"✓ Loaded PDF from: {pdf_file_path}")
    
    # 2. Extract chunks from PDF
    logger.info("*********** Extract chunks from PDF ***********")
    chunks_pdf = extract_from_pdf(file_like)
    assert len(chunks_pdf) > 0, "Should extract at least one chunk from PDF"
    logger.info(f"✓ Extracted {len(chunks_pdf)} chunks from PDF")
    
    # Log first few chunks for verification
    for i, chunk in enumerate(chunks_pdf[:3], start=1):
        logger.info(f"Chunk {i} preview: {chunk.page_content[:100]}...")
    
    # 3. Extract entities and relationships
    logger.info("*********** Extract entities and relationships ***********")
    llm = OllamaModel()
    final_entities = em.extract_entities_and_relationships_from_chunks(
        chunks_pdf, llm, max_chunks=2  # Limited for testing
    )
    
    entities = final_entities["entities"]
    relationships = final_entities["relationships"]
    
    assert len(entities) > 0, "Should extract at least one entity"
    logger.info(f"✓ Extracted {len(entities)} entities")
    logger.info(f"✓ Extracted {len(relationships)} relationships")
    
    # Log extracted entities
    for name, description in list(entities.items())[:5]:
        logger.info(f"Entity: {name}")
        logger.info(f"  Description: {description[:100]}...")
    
    # 4. Store in database
    logger.info("*********** Store entities in database ***********")
    entity_count = 0
    for name, description in entities.items():
        try:
            result = dbm.create_entity(name, description)
            if result != "Entity already exists":
                entity_count += 1
                logger.info(f"✓ Stored entity: {name}")
            else:
                logger.info(f"↷ Entity already exists: {name}")
        except Exception as e:
            logger.warning(f"Could not store entity {name}: {e}")
    
    relationship_count = 0
    for subject, predicate, obj in relationships:
        try:
            dbm.create_relationship(subject, predicate, obj)
            relationship_count += 1
            logger.info(f"✓ Stored relationship: {subject} -> {predicate} -> {obj}")
        except Exception as e:
            logger.warning(f"Could not store relationship: {e}")
    
    # 5. Verify storage
    stored_entities = dbm.get_entity_count()
    stored_relationships = dbm.get_relationship_count()
    
    assert stored_entities >= entity_count, "Entities should be stored"
    assert stored_relationships >= relationship_count, "Relationships should be stored"
    
    logger.info(f"✓ Final counts: {stored_entities} entities, {stored_relationships} relationships")
    
    # 6. Verify we can retrieve data
    logger.info("*********** Verify data retrieval ***********")
    all_entities = dbm.get_all_entities()
    assert len(all_entities) == stored_entities, "Should retrieve all stored entities"
    logger.info(f"✓ Successfully retrieved {len(all_entities)} entities from database")
    
    all_relationships = dbm.get_all_relationships()
    assert len(all_relationships) == stored_relationships, "Should retrieve all stored relationships"
    logger.info(f"✓ Successfully retrieved {len(all_relationships)} relationships from database")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--log-cli-level=INFO"])