import database as db
import logging

logger = logging.getLogger(__name__)

class DBManager:
    ### ENTITIES ###
    # Create
    @staticmethod
    def create_entity(name: str, description: str) -> str:
        if db.get_entity_by_name(name):
            logger.warning(f"Entity '{name}' already exists. Skipping creation.")
            return "Entity already exists"
        return db.create_entity(name, description)

    # Read
    @staticmethod
    def get_all_entities() -> list:
        return db.get_all_entities()

    @staticmethod
    def get_entity_by_name(name: str) -> dict:
        return db.get_entity_by_name(name)

    @staticmethod
    def get_entity_count() -> int:
        return db.get_entity_count()

    # Update
    @staticmethod
    def update_entity_description(name: str, new_description: str) -> None:
        db.update_entity_description(name, new_description)

    @staticmethod
    def update_entity_name(old_name: str, new_name: str) -> None:
        """Update the name of an entity both in entities and relationships collection to keep it consistant."""
        db.update_entity_name(old_name, new_name)
        db.update_relationship_object(old_name, new_name)
        db.update_relationship_subject(old_name, new_name)

    # Delete
    @staticmethod
    def delete_entity(name: str) -> None:
        db.delete_relationships_by_entity(name)
        db.delete_entity(name)
        
    @staticmethod
    def drop_collection_entities() -> None:
        db.drop_collection_entities()
    
    
    ### RELATIONSHIPS ###
    # Create
    @staticmethod
    def create_relationship(subject: str, predicate: str, obj: str) -> str:
        if not db.get_entity_by_name(subject):
            return
            db.create_entity(subject, "")
        if not db.get_entity_by_name(obj):
            return
            db.create_entity(obj, "")
        
        return db.create_relationship(subject, predicate, obj)
    
    # Read
    @staticmethod
    def get_all_relationships() -> list:
        return db.get_all_relationships()
    
    @staticmethod
    def get_relationships_by_entity(entity_name: str) -> list:
        """Get relationships where the entity is either subject or object."""
        return db.get_relationships_by_entity(entity_name)
    
    @staticmethod
    def get_relationship_count() -> int:
        return db.get_relationship_count()  
    
    # Update
    @staticmethod
    def update_relationship_subject(old_subject: str, new_subject: str) -> None:
        db.update_relationship_subject(old_subject, new_subject)
    @staticmethod
    def update_relationship_object(old_object: str, new_object: str) -> None:
        db.update_relationship_object(old_object, new_object)
    @staticmethod
    def update_relationship_predicate(subject: str, object: str, new_predicate: str) -> None:
        db.update_relationship_predicate(subject, object, new_predicate)
   
   # Delete
    @staticmethod
    def delete_relationship(subject: str, obj: str) -> None:
        """Delete a relationship by subject and object."""
        db.delete_relationship(subject, obj)
    @staticmethod
    def delete_relationships_by_entity(entity_name: str) -> None:
        """Delete all relationships connected to the selected entity."""
        db.delete_relationships_by_entity(entity_name)
    @staticmethod
    def drop_collection_relationships() -> None:
        db.drop_collection_relationships()