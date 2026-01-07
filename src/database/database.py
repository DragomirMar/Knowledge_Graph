from typing import List, Dict, Any
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the project root directory to load .env
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables based on ENVIRONMENT setting
environment = os.getenv('ENVIRONMENT', 'production')

if environment == 'test':
    env_file = PROJECT_ROOT / '.env.test'
    load_dotenv(env_file)
    print(f"Loading TEST environment from: {env_file}")
else:
    env_file = PROJECT_ROOT / '.env'
    load_dotenv(env_file) 
    print(f"Loading PRODUCTION environment from: {env_file}")

# Get configuration from environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'knowledge_graph')

print(f"Database: {MONGODB_DATABASE}")
print(f"MongoDB URI: {MONGODB_URI}")

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DATABASE]
entities_collection = db["entities"]
relationships_collection = db["relationships"]

# Verify connection
try:
    client.admin.command('ping')
    print(f"✓ Successfully connected to MongoDB database: {MONGODB_DATABASE}")
except Exception as e:
    print(f"✗ Failed to connect to MongoDB: {e}")
    raise


### ENTITY DATABASE FUNCTIONS ###
# CREATE
def create_entity(name: str, description: str) -> str:
    entity_doc = {
        "name": name.strip().title(),
        "description": description.strip(),
    }
    result = entities_collection.insert_one(entity_doc)
    return str(result.inserted_id)

# READ 
def get_all_entities() -> List[Dict[str, Any]]:
    entities = list(entities_collection.find())
    for entity in entities:
        entity["_id"] = str(entity["_id"])
    return entities

def get_entity_by_name(name: str) -> Dict[str, Any]:
    entity = entities_collection.find_one({"name": name.strip().title()})
    if entity:
        entity["_id"] = str(entity["_id"])
    return entity if entity else {}

def get_entity_count() -> int:
    return entities_collection.count_documents({})

# UPDATE
def update_entity_description(name: str, new_description: str) -> None:
    entities_collection.update_one(
        {"name": name.strip().title()},
        {"$set": {"description": new_description.strip()}}
    )
    
def update_entity_name(old_name: str, new_name: str) -> None:
    entities_collection.update_one(
        {"name": old_name.strip().title()},
        {"$set": {"name": new_name.strip().title()}}
    )

# DELETE
def delete_entity(name: str) -> None:
    return entities_collection.delete_one({"name": name.strip().title()})

def drop_collection_entities():
    return entities_collection.drop()

""" 
Example Entity:
    {
        name: "Liverpool FC",
        description: "A football club based in Liverpool, England."
    }
"""

### RELATIONSHIPS DATABASE FUNCTIONS ###
# CREATE
def create_relationship(subject: str, predicate: str, obj: str) -> str:
    relationship_doc = {
        "subject": subject.strip().title(),
        "predicate": predicate.strip(),
        "object": obj.strip().title(),
    }
    result = relationships_collection.insert_one(relationship_doc)
    return str(result.inserted_id)

# READ
def get_all_relationships() -> List[Dict[str, Any]]:
    relationships = list(relationships_collection.find())
    for relationship in relationships:
        relationship["_id"] = str(relationship["_id"])
    return relationships

def get_relationships_by_entity(entity_name: str) -> List[Dict[str, Any]]:
    name = entity_name.strip().title()
    relationships = list(relationships_collection.find({
        "$or": [
            {"subject": name},
            {"object": name}
        ]
    }))
    for relationship in relationships:
        relationship["_id"] = str(relationship["_id"])
    return relationships

def get_relationship_count() -> int:
    return relationships_collection.count_documents({})

# UPDATE
def update_relationship_subject(old_subject: str, new_subject: str) -> None:
    relationships_collection.update_many(
        {"subject": old_subject.strip().title()},
        {"$set": {"subject": new_subject.strip().title()}}
    )

def update_relationship_object(old_object: str, new_object: str) -> None:
    relationships_collection.update_many(
        {"object": old_object.strip().title()},
        {"$set": {"object": new_object.strip().title()}}
    )   
    
def update_relationship_predicate(subject: str, object: str, new_predicate: str) -> None:
    relationships_collection.update_many(
        {"subject": subject.strip().title(), "object": object.strip().title()},
        {"$set": {"predicate": new_predicate.strip()}}
    )
    
# DELETE
def delete_relationship(subject: str, obj: str) -> None:
    """Deletes a relationship by subject and object"""
    return relationships_collection.delete_one({
        "subject": subject.strip().title(),
        "object": obj.strip().title()
    })
    
def delete_relationships_by_entity(entity_name: str) -> None:
    """Deletes all relationships where the entity is either a subject or an object"""
    relationships_collection.delete_many({
        "$or": [
            {"subject": entity_name.strip().title()},
            {"object": entity_name.strip().title()}
        ]
    })
   
def drop_collection_relationships():
    return relationships_collection.drop()

""" 
Example relationship:
    {
        subject: "Liverpool FC",
        predicate: "has",
        object: "Trent Alexander-Arnold"
    }
"""