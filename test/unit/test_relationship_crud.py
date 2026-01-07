import pytest
import logging
from bson import ObjectId
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.database import (
    create_relationship, get_all_relationships, get_relationships_by_entity,
    get_relationship_count, update_relationship_subject, update_relationship_object,
    update_relationship_predicate, delete_relationship, delete_relationships_by_entity,
    create_entity, delete_entity
)

logger = logging.getLogger(__name__)


@pytest.fixture
def relationship_cleanup():
    test_entities = [
        ("Test Liverpool Fc", "Test football club from Liverpool"),
        ("Test Trent Alexander-Arnold", "Test English footballer"),
        ("Test Transfer Fee", "Test monetary amount for transfers"),
        ("Test Real Madrid", "Test Spanish football club"),
        ("Test Barcelona", "Test Catalan football club")
    ]
    
    created_entities = []
    for name, desc in test_entities:
        create_entity(name, desc)
        created_entities.append(name)
        logger.info(f"Created test entity: {name}")
    
    relationships_to_cleanup = []
    
    yield relationships_to_cleanup
    
    # Cleanup relationships
    logger.info(f"Cleaning up {len(relationships_to_cleanup)} relationships")
    for subject, obj in relationships_to_cleanup:
        try:
            delete_relationship(subject, obj)
            logger.info(f"✓ Cleaned up relationship: {subject} -> {obj}")
        except Exception as e:
            logger.warning(f"Could not clean up relationship {subject} -> {obj}: {e}")
    
    # Cleanup entities
    for entity_name in created_entities:
        try:
            delete_entity(entity_name)
            logger.info(f"✓ Cleaned up entity: {entity_name}")
        except Exception as e:
            logger.warning(f"Could not clean up entity {entity_name}: {e}")


def test_database_connection():
    """Test that database connection is working"""
    logger.info("--- Testing Database Connection for Relationships ---")
    try:
        count = get_relationship_count()
        logger.info(f"✓ Database connection successful. Current relationship count: {count}")
        assert isinstance(count, int)
        assert count >= 0
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        pytest.fail(f"Database connection failed: {e}")


def test_create_relationship(relationship_cleanup):
    logger.info("--- Testing CREATE Relationship ---")
    
    subject = "Test Liverpool Fc"
    predicate = "has_player"
    obj = "Test Trent Alexander-Arnold"
    relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
    
    # Test creation
    relationship_id = create_relationship(subject, predicate, obj)
    logger.info(f"Created relationship with ID: {relationship_id}")
    
    # Verify creation
    assert relationship_id is not None
    assert ObjectId.is_valid(relationship_id)
    
    # Verify by getting all relationships
    all_relationships = get_all_relationships()
    created_relationship = None
    for rel in all_relationships:
        if (rel["subject"] == subject.strip().title() and 
            rel["object"] == obj.strip().title() and
            rel["predicate"] == predicate.strip()):
            created_relationship = rel
            break
    
    logger.info(f"Retrieved created relationship: {created_relationship}")
    assert created_relationship is not None
    assert created_relationship["subject"] == subject.strip().title()
    assert created_relationship["predicate"] == predicate.strip()
    assert created_relationship["object"] == obj.strip().title()
    assert created_relationship["_id"] == relationship_id
    
    # Log database change
    count_after_create = get_relationship_count()
    logger.info(f"Relationship count after creation: {count_after_create}")


def test_get_all_relationships(relationship_cleanup):
    logger.info("--- Testing GET All Relationships ---")
    
    initial_relationships = get_all_relationships()
    initial_count = len(initial_relationships)
    logger.info(f"Initial relationships count: {initial_count}")
    
    # Create test relationships
    test_relationships = [
        ("Test Liverpool Fc", "has_player", "Test Trent Alexander-Arnold"),
        ("Test Real Madrid", "wants", "Test Trent Alexander-Arnold"),
        ("Test Barcelona", "offers", "Test Transfer Fee"),
        ("Test Liverpool Fc", "demands", "Test Transfer Fee")
    ]
    
    for subject, predicate, obj in test_relationships:
        create_relationship(subject, predicate, obj)
        relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
        logger.info(f"Added test relationship: {subject} -> {predicate} -> {obj}")
    
    # Get all relationships after additions
    all_relationships = get_all_relationships()
    logger.info(f"Total relationships after additions: {len(all_relationships)}")
    
    assert len(all_relationships) == initial_count + len(test_relationships)
    assert isinstance(all_relationships, list)
    
    # Verify all test relationships are present
    relationship_tuples = [(rel["subject"], rel["predicate"], rel["object"]) for rel in all_relationships]
    for subject, predicate, obj in test_relationships:
        expected_tuple = (subject.strip().title(), predicate.strip(), obj.strip().title())
        assert expected_tuple in relationship_tuples, f"Relationship {expected_tuple} not found"


def test_get_relationships_by_entity(relationship_cleanup):
    logger.info("--- Testing GET Relationships by Entity ---")
    
    entity_name = "Test Liverpool Fc"
    
    test_relationships = [
        (entity_name, "has_player", "Test Trent Alexander-Arnold"),
        (entity_name, "competes_with", "Test Real Madrid"),
        ("Test Barcelona", "rivals", entity_name),
        ("Test Transfer Fee", "belongs_to", entity_name)
    ]
    
    for subject, predicate, obj in test_relationships:
        create_relationship(subject, predicate, obj)
        relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
        logger.info(f"Created relationship: {subject} -> {predicate} -> {obj}")
    
    # Test retrieving relationships for the entity
    entity_relationships = get_relationships_by_entity(entity_name)
    logger.info(f"Found {len(entity_relationships)} relationships for {entity_name}")
    
    for rel in entity_relationships:
        logger.info(f"  {rel['subject']} -> {rel['predicate']} -> {rel['object']}")
    
    # Verify count
    assert len(entity_relationships) == len(test_relationships)
    assert isinstance(entity_relationships, list)
    
    # Verify each relationship involves this entity
    for rel in entity_relationships:
        entity_involved = (rel["subject"] == entity_name.strip().title() or 
                         rel["object"] == entity_name.strip().title())
        assert entity_involved, f"Relationship doesn't involve {entity_name}: {rel}"


def test_get_relationship_count(relationship_cleanup):
    logger.info("--- Testing GET Relationship Count ---")
    
    initial_count = get_relationship_count()
    logger.info(f"Initial count: {initial_count}")
    
    test_relationships = [
        ("Test Barcelona", "has", "Test Transfer Fee"),
        ("Test Real Madrid", "wants", "Test Transfer Fee"),
        ("Test Liverpool Fc", "holds", "Test Transfer Fee")
    ]
    
    for i, (subject, predicate, obj) in enumerate(test_relationships):
        create_relationship(subject, predicate, obj)
        relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
        current_count = get_relationship_count()
        logger.info(f"Count after creating relationship {i+1}: {current_count}")
    
    final_count = get_relationship_count()
    assert final_count == initial_count + len(test_relationships)
    logger.info(f"Final count after all creations: {final_count}")


def test_update_relationship_subject(relationship_cleanup):
    logger.info("--- Testing UPDATE Relationship Subject ---")
    
    original_subject = "Test Liverpool Fc"
    new_subject = "Test Liverpool Football Club"
    predicate = "has_player"
    obj = "Test Trent Alexander-Arnold"
    
    # Create test entity for new subject
    create_entity(new_subject, "Updated Liverpool FC")
    
    relationship_cleanup.append((original_subject.strip().title(), obj.strip().title()))
    relationship_cleanup.append((new_subject.strip().title(), obj.strip().title()))
    
    # Create relationship
    create_relationship(original_subject, predicate, obj)
    logger.info(f"Created relationship: {original_subject} -> {predicate} -> {obj}")
    
    # Update subject
    update_relationship_subject(original_subject, new_subject)
    logger.info(f"Updated subject from '{original_subject}' to '{new_subject}'")
    
    # Verify update
    updated_relationships = get_relationships_by_entity(new_subject)
    old_relationships = get_relationships_by_entity(original_subject)
    
    logger.info(f"Relationships with new subject: {len(updated_relationships)}")
    logger.info(f"Relationships with old subject: {len(old_relationships)}")
    
    # Should find relationship with new subject
    assert len(updated_relationships) >= 1
    found_updated = any(rel["subject"] == new_subject.strip().title() and 
                       rel["object"] == obj.strip().title() and
                       rel["predicate"] == predicate.strip()
                       for rel in updated_relationships)
    assert found_updated, "Updated relationship not found"
    
    # Should not find relationship with old subject as subject
    found_old = any(rel["subject"] == original_subject.strip().title() and 
                   rel["object"] == obj.strip().title()
                   for rel in old_relationships)
    assert not found_old, "Old subject relationship still exists"
    
    # Cleanup the new entity
    delete_entity(new_subject)


def test_update_relationship_object(relationship_cleanup):
    logger.info("--- Testing UPDATE Relationship Object ---")
    
    subject = "Test Real Madrid"
    predicate = "wants"
    original_object = "Test Trent Alexander-Arnold"
    new_object = "Test Alexander-Arnold"
    
    # Create test entity for new object
    create_entity(new_object, "Updated player name")
    
    relationship_cleanup.append((subject.strip().title(), original_object.strip().title()))
    relationship_cleanup.append((subject.strip().title(), new_object.strip().title()))
    
    # Create relationship
    create_relationship(subject, predicate, original_object)
    logger.info(f"Created relationship: {subject} -> {predicate} -> {original_object}")
    
    # Update object
    update_relationship_object(original_object, new_object)
    logger.info(f"Updated object from '{original_object}' to '{new_object}'")
    
    # Verify update
    updated_relationships = get_relationships_by_entity(new_object)
    old_relationships = get_relationships_by_entity(original_object)
    
    logger.info(f"Relationships with new object: {len(updated_relationships)}")
    logger.info(f"Relationships with old object: {len(old_relationships)}")
    
    # Should find relationship with new object
    found_updated = any(rel["subject"] == subject.strip().title() and 
                       rel["object"] == new_object.strip().title() and
                       rel["predicate"] == predicate.strip()
                       for rel in updated_relationships)
    assert found_updated, "Updated relationship not found"
    
    # Cleanup the new entity
    delete_entity(new_object)


def test_update_relationship_predicate(relationship_cleanup):
    """Test updating relationship predicate"""
    logger.info("--- Testing UPDATE Relationship Predicate ---")
    
    subject = "Test Barcelona"
    obj = "Test Transfer Fee"
    original_predicate = "offers"
    new_predicate = "demands"
    
    relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
    
    # Create relationship
    create_relationship(subject, original_predicate, obj)
    logger.info(f"Created relationship: {subject} -> {original_predicate} -> {obj}")
    
    # Update predicate
    update_relationship_predicate(subject, obj, new_predicate)
    logger.info(f"Updated predicate from '{original_predicate}' to '{new_predicate}'")
    
    # Verify update
    entity_relationships = get_relationships_by_entity(subject)
    
    found_updated = any(rel["subject"] == subject.strip().title() and 
                       rel["object"] == obj.strip().title() and
                       rel["predicate"] == new_predicate.strip()
                       for rel in entity_relationships)
    
    found_old = any(rel["subject"] == subject.strip().title() and 
                   rel["object"] == obj.strip().title() and
                   rel["predicate"] == original_predicate.strip()
                   for rel in entity_relationships)
    
    logger.info(f"Found updated predicate: {found_updated}")
    logger.info(f"Found old predicate: {found_old}")
    
    assert found_updated, "Updated predicate not found"
    assert not found_old, "Old predicate still exists"


def test_delete_relationship(relationship_cleanup):
    logger.info("--- Testing DELETE Relationship ---")
    
    subject = "Test Real Madrid"
    predicate = "competes_with"
    obj = "Test Barcelona"
    
    # Create relationship
    relationship_id = create_relationship(subject, predicate, obj)
    logger.info(f"Created relationship for deletion: {subject} -> {predicate} -> {obj} (ID: {relationship_id})")
    
    # Verify existence before deletion
    relationships_before = get_relationships_by_entity(subject)
    count_before = get_relationship_count()
    logger.info(f"Relationships for {subject} before deletion: {len(relationships_before)}")
    logger.info(f"Total count before deletion: {count_before}")
    
    found_before = any(rel["subject"] == subject.strip().title() and 
                      rel["object"] == obj.strip().title()
                      for rel in relationships_before)
    assert found_before, "Relationship should exist before deletion"
    
    # Delete relationship
    result = delete_relationship(subject, obj)
    logger.info(f"Deletion result: {result.deleted_count} document(s) deleted")
    
    # Verify deletion
    relationships_after = get_relationships_by_entity(subject)
    count_after = get_relationship_count()
    logger.info(f"Relationships for {subject} after deletion: {len(relationships_after)}")
    logger.info(f"Total count after deletion: {count_after}")
    
    found_after = any(rel["subject"] == subject.strip().title() and 
                     rel["object"] == obj.strip().title()
                     for rel in relationships_after)
    
    assert not found_after, "Relationship should not exist after deletion"
    assert count_after == count_before - 1
    assert result.deleted_count == 1


def test_delete_relationships_by_entity(relationship_cleanup):
    logger.info("--- Testing DELETE Relationships by Entity ---")
    
    target_entity = "Test Liverpool Fc"
    
    test_relationships = [
        (target_entity, "has", "Test Trent Alexander-Arnold"),
        (target_entity, "competes_with", "Test Real Madrid"),
        ("Test Barcelona", "rivals", target_entity),
        ("Test Transfer Fee", "belongs_to", target_entity)
    ]
    
    for subject, predicate, obj in test_relationships:
        create_relationship(subject, predicate, obj)
        logger.info(f"Created relationship: {subject} -> {predicate} -> {obj}")
    
    # Verify relationships exist
    relationships_before = get_relationships_by_entity(target_entity)
    count_before = get_relationship_count()
    logger.info(f"Relationships for {target_entity} before deletion: {len(relationships_before)}")
    logger.info(f"Total count before deletion: {count_before}")
    
    assert len(relationships_before) == len(test_relationships)
    
    # Delete all relationships for entity
    delete_relationships_by_entity(target_entity)
    logger.info(f"Deleted all relationships for {target_entity}")
    
    # Verify deletion
    relationships_after = get_relationships_by_entity(target_entity)
    count_after = get_relationship_count()
    logger.info(f"Relationships for {target_entity} after deletion: {len(relationships_after)}")
    logger.info(f"Total count after deletion: {count_after}")
    
    assert len(relationships_after) == 0
    assert count_after == count_before - len(test_relationships)


def test_crud_operations_integration(relationship_cleanup):
    """Integration test covering all CRUD operations"""
    logger.info("--- Testing CRUD Integration ---")
    
    subject = "Test Inter Milan"
    obj = "Test Transfer Fee"
    original_predicate = "offers"
    updated_predicate = "demands"
    new_subject = "Test Internazionale"
    
    # Create additional test entities
    create_entity("Test Inter Milan", "Italian football club")
    create_entity(new_subject, "Updated Italian club name")
    
    relationship_cleanup.append((subject.strip().title(), obj.strip().title()))
    relationship_cleanup.append((new_subject.strip().title(), obj.strip().title()))
    
    initial_count = get_relationship_count()
    logger.info(f"Starting integration test with count: {initial_count}")
    
    # CREATE
    relationship_id = create_relationship(subject, original_predicate, obj)
    logger.info(f"✓ Created: {subject} -> {original_predicate} -> {obj}")
    assert get_relationship_count() == initial_count + 1
    
    # READ - by entity
    relationships = get_relationships_by_entity(subject)
    logger.info(f"✓ Read: Found {len(relationships)} relationships for {subject}")
    found = any(rel["_id"] == relationship_id for rel in relationships)
    assert found, "Created relationship should be found"
    
    # UPDATE predicate
    update_relationship_predicate(subject, obj, updated_predicate)
    relationships = get_relationships_by_entity(subject)
    found_updated_predicate = any(rel["predicate"] == updated_predicate for rel in relationships)
    logger.info(f"✓ Updated predicate: {found_updated_predicate}")
    assert found_updated_predicate
    
    # UPDATE subject
    update_relationship_subject(subject, new_subject)
    old_relationships = get_relationships_by_entity(subject)
    new_relationships = get_relationships_by_entity(new_subject)
    logger.info(f"✓ Updated subject: old={len(old_relationships)}, new={len(new_relationships)}")
    
    # Verify old subject has no relationships and new subject has them
    found_with_old_subject = any(rel["subject"] == subject.strip().title() and 
                               rel["object"] == obj.strip().title()
                               for rel in old_relationships)
    found_with_new_subject = any(rel["subject"] == new_subject.strip().title() and 
                               rel["object"] == obj.strip().title()
                               for rel in new_relationships)
    
    assert not found_with_old_subject, "Should not find relationship with old subject"
    assert found_with_new_subject, "Should find relationship with new subject"
    
    # COUNT
    assert get_relationship_count() == initial_count + 1
    logger.info(f"✓ Count maintained at: {get_relationship_count()}")
    
    # Cleanup the extra entities
    delete_entity("Test Inter Milan")
    delete_entity(new_subject)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--log-cli-level=INFO"])