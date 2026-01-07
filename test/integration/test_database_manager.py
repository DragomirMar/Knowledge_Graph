import pytest
import logging
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from database.database_manager import DBManager as dbm

logger = logging.getLogger(__name__)


@pytest.fixture
def test_entities():
    """Track created entities for cleanup"""
    entities = []
    yield entities
    # Cleanup
    for entity_name in entities:
        try:
            dbm.delete_entity(entity_name)
        except:
            pass


def test_entity_name_update_cascades_to_relationships(test_entities):
    """Test that updating entity name updates all related relationships"""
    logger.info("Testing entity name cascade update")
    
    entity_a = "Test Entity A"
    entity_b = "Test Entity B"
    new_name = "Test Entity A Updated"
    
    test_entities.extend([entity_a, entity_b, new_name])
    
    # Create entities
    dbm.create_entity(entity_a, "Description A")
    dbm.create_entity(entity_b, "Description B")
    
    # Create relationships with entity_a as both subject and object
    dbm.create_relationship(entity_a, "relates to", entity_b)
    dbm.create_relationship(entity_b, "connects with", entity_a)
    
    # Update entity_a name
    dbm.update_entity_name(entity_a, new_name)
    
    # Verify relationships were updated
    relationships_new = dbm.get_relationships_by_entity(new_name)
    relationships_old = dbm.get_relationships_by_entity(entity_a)
    
    logger.info(f"Relationships with new name: {len(relationships_new)}")
    logger.info(f"Relationships with old name: {len(relationships_old)}")
    
    # Should find both relationships with new name
    assert len(relationships_new) == 2
    # Should not find any with old name
    assert len(relationships_old) == 0
    
    # Verify specific relationships
    subjects = [rel['subject'] for rel in relationships_new]
    objects = [rel['object'] for rel in relationships_new]
    
    assert new_name.strip().title() in subjects or new_name.strip().title() in objects


def test_delete_entity_cascades_to_relationships(test_entities):
    """Test that deleting entity deletes all related relationships"""
    logger.info("Testing entity deletion cascade")
    
    entity_a = "Test Delete Entity A"
    entity_b = "Test Delete Entity B"
    entity_c = "Test Delete Entity C"
    
    test_entities.extend([entity_a, entity_b, entity_c])
    
    # Create entities
    dbm.create_entity(entity_a, "Description A")
    dbm.create_entity(entity_b, "Description B")
    dbm.create_entity(entity_c, "Description C")
    
    # Create relationships
    dbm.create_relationship(entity_a, "relates to", entity_b)
    dbm.create_relationship(entity_a, "connects with", entity_c)
    dbm.create_relationship(entity_b, "links to", entity_a)
    
    initial_rel_count = dbm.get_relationship_count()
    logger.info(f"Initial relationship count: {initial_rel_count}")
    
    # Delete entity_a
    dbm.delete_entity(entity_a)
    
    # Verify entity is deleted
    entity = dbm.get_entity_by_name(entity_a)
    assert entity == {}
    
    # Verify all relationships involving entity_a are deleted
    relationships = dbm.get_relationships_by_entity(entity_a)
    assert len(relationships) == 0
    
    # Verify total count decreased by 3 (all relationships with entity_a)
    final_rel_count = dbm.get_relationship_count()
    logger.info(f"Final relationship count: {final_rel_count}")
    assert final_rel_count == initial_rel_count - 3


def test_create_entity_prevents_duplicates(test_entities):
    """Test that creating duplicate entity returns appropriate message"""
    entity_name = "Test Duplicate Entity"
    test_entities.append(entity_name)
    
    # Create entity first time
    result1 = dbm.create_entity(entity_name, "First description")
    assert result1 != "Entity already exists"
    
    # Try to create again
    result2 = dbm.create_entity(entity_name, "Second description")
    assert result2 == "Entity already exists"
    
    # Verify only one entity exists
    entities = dbm.get_all_entities()
    matching = [e for e in entities if e['name'] == entity_name.strip().title()]
    assert len(matching) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])