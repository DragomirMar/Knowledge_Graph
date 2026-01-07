import pytest
import logging
from bson import ObjectId
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.database import (
    create_entity, get_all_entities, get_entity_by_name, 
    get_entity_count, update_entity_description, 
    update_entity_name, delete_entity
)

logger = logging.getLogger(__name__)


@pytest.fixture
def entity_cleanup():
    entity_names = []
    yield entity_names
    # Cleanup after test
    logger.info(f"Cleaning up {len(entity_names)} test entities")
    for entity_name in entity_names:
        try:
            entity = get_entity_by_name(entity_name)
            if entity:
                delete_entity(entity_name)
                logger.info(f"✓ Cleaned up: {entity_name}")
        except Exception as e:
            logger.warning(f"Could not clean up {entity_name}: {e}")


def test_database_connection():
    """Test that database connection is working"""
    logger.info("--- Testing Database Connection ---")
    try:
        count = get_entity_count()
        logger.info(f"✓ Database connection successful. Current entity count: {count}")
        assert isinstance(count, int)
        assert count >= 0
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        pytest.fail(f"Database connection failed: {e}")


def test_create_entity(entity_cleanup):
    logger.info("--- Testing CREATE Entity ---")
    
    name = "Test Liverpool FC"
    description = "A test football club for testing purposes"
    entity_cleanup.append(name.strip().title())
    
    # Test creation
    entity_id = create_entity(name, description)
    logger.info(f"Created entity with ID: {entity_id}")
    
    # Verify creation
    assert entity_id is not None
    assert ObjectId.is_valid(entity_id)
    
    created_entity = get_entity_by_name(name)
    logger.info(f"Retrieved created entity: {created_entity}")
    
    assert created_entity["name"] == name.strip().title()
    assert created_entity["description"] == description.strip()
    assert created_entity["_id"] == entity_id
    
    # Log database change
    count_after_create = get_entity_count()
    logger.info(f"Entity count after creation: {count_after_create}")


def test_get_all_entities(entity_cleanup):
    logger.info("--- Testing GET All Entities ---")
    
    initial_entities = get_all_entities()
    initial_count = len(initial_entities)
    logger.info(f"Initial entities count: {initial_count}")
    
    # Create test entities
    test_entities = [
        ("Test Arsenal", "Test London football club"),
        ("Test Chelsea", "Test West London club"),
        ("Test Tottenham", "Test North London club")
    ]
    
    for name, desc in test_entities:
        create_entity(name, desc)
        entity_cleanup.append(name.strip().title())
        logger.info(f"Added test entity: {name}")
    
    # Get all entities after additions
    all_entities = get_all_entities()
    logger.info(f"Total entities after additions: {len(all_entities)}")
    
    assert len(all_entities) == initial_count + len(test_entities)
    assert isinstance(all_entities, list)
    
    # Verify all test entities are present
    entity_names = [entity["name"] for entity in all_entities]
    for name, _ in test_entities:
        assert name.strip().title() in entity_names


def test_get_entity_by_name(entity_cleanup):
    logger.info("--- Testing GET Entity by Name ---")
    
    name = "Test Real Madrid"
    description = "Spanish football club for testing"
    entity_cleanup.append(name.strip().title())
    
    # Create entity
    create_entity(name, description)
    logger.info(f"Created entity: {name}")
    
    # Test successful retrieval
    entity = get_entity_by_name(name)
    logger.info(f"Retrieved entity: {entity}")
    
    assert entity["name"] == name.strip().title()
    assert entity["description"] == description.strip()
    assert "_id" in entity


def test_get_entity_count(entity_cleanup):
    logger.info("--- Testing GET Entity Count ---")
    
    initial_count = get_entity_count()
    logger.info(f"Initial count: {initial_count}")
    
    # Create test entities
    test_names = ["Test Barcelona", "Test Valencia", "Test Sevilla"]
    for name in test_names:
        create_entity(name, f"Test description for {name}")
        entity_cleanup.append(name.strip().title())
        current_count = get_entity_count()
        logger.info(f"Count after creating {name}: {current_count}")
    
    final_count = get_entity_count()
    assert final_count == initial_count + len(test_names)
    logger.info(f"Final count after all creations: {final_count}")


def test_update_entity_description(entity_cleanup):
    logger.info("--- Testing UPDATE Entity Description ---")
    
    name = "Test Bayern Munich"
    original_description = "Original German club description"
    new_description = "Updated German football club description"
    entity_cleanup.append(name.strip().title())
    
    # Create entity
    create_entity(name, original_description)
    logger.info(f"Created entity with description: {original_description}")
    
    # Update description
    update_entity_description(name, new_description)
    logger.info(f"Updated description to: {new_description}")
    
    # Verify update
    updated_entity = get_entity_by_name(name)
    logger.info(f"Retrieved updated entity: {updated_entity}")
    
    assert updated_entity["description"] == new_description.strip()
    assert updated_entity["name"] == name.strip().title()


def test_update_entity_name(entity_cleanup):
    logger.info("--- Testing UPDATE Entity Name ---")
    
    original_name = "Test AC Milan"
    new_name = "Test Ac Milano"
    description = "Italian football club for testing"
    entity_cleanup.append(original_name.strip().title())
    entity_cleanup.append(new_name.strip().title())
    
    # Create entity
    create_entity(original_name, description)
    logger.info(f"Created entity with name: {original_name}")
    
    # Update name
    update_entity_name(original_name, new_name)
    logger.info(f"Updated name from '{original_name}' to '{new_name}'")
    
    # Verify update
    old_entity = get_entity_by_name(original_name)
    new_entity = get_entity_by_name(new_name)
    
    logger.info(f"Old name search result: {old_entity}")
    logger.info(f"New name search result: {new_entity}")
    
    assert old_entity == {}
    assert new_entity["name"] == new_name.strip().title()
    assert new_entity["description"] == description.strip()


def test_delete_entity():
    logger.info("--- Testing DELETE Entity ---")
    
    name = "Test Juventus"
    description = "Italian club to be deleted"
    
    # Create entity
    entity_id = create_entity(name, description)
    logger.info(f"Created entity for deletion: {name} (ID: {entity_id})")
    
    # Verify existence before deletion
    entity_before = get_entity_by_name(name)
    count_before = get_entity_count()
    logger.info(f"Entity before deletion: {entity_before}")
    logger.info(f"Count before deletion: {count_before}")
    
    assert entity_before != {}
    
    # Delete entity
    result = delete_entity(name)
    logger.info(f"Deletion result: {result.deleted_count} document(s) deleted")
    
    # Verify deletion
    entity_after = get_entity_by_name(name)
    count_after = get_entity_count()
    logger.info(f"Entity after deletion: {entity_after}")
    logger.info(f"Count after deletion: {count_after}")
    
    assert entity_after == {}
    assert count_after == count_before - 1
    assert result.deleted_count == 1


def test_crud_operations_integration(entity_cleanup):
    """Integration test covering all CRUD operations"""
    logger.info("--- Testing CRUD Integration ---")
    
    name = "Test Inter Milan"
    original_desc = "Original Italian club"
    updated_desc = "Updated Italian football club"
    new_name = "Test Internazionale"
    
    entity_cleanup.append(name.strip().title())
    entity_cleanup.append(new_name.strip().title())
    
    initial_count = get_entity_count()
    logger.info(f"Starting integration test with count: {initial_count}")
    
    # CREATE
    entity_id = create_entity(name, original_desc)
    logger.info(f"Created: {name}")
    assert get_entity_count() == initial_count + 1
    
    # READ
    entity = get_entity_by_name(name)
    logger.info(f"Read: {entity['name']}")
    assert entity["_id"] == entity_id
    
    # UPDATE description
    update_entity_description(name, updated_desc)
    entity = get_entity_by_name(name)
    logger.info(f"Updated description: {entity['description']}")
    assert entity["description"] == updated_desc
    
    # UPDATE name
    update_entity_name(name, new_name)
    entity = get_entity_by_name(new_name)
    logger.info(f"Updated name: {entity['name']}")
    assert entity["name"] == new_name.strip().title()
    
    # Verify old name doesn't exist
    old_entity = get_entity_by_name(name)
    assert old_entity == {}
    logger.info(f"Verified old name removed")
    
    # COUNT should still be +1
    assert get_entity_count() == initial_count + 1
    logger.info(f"Count maintained at: {get_entity_count()}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])