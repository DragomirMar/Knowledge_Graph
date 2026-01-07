from collections import defaultdict
import logging
import re
from llm import OllamaModel

logger = logging.getLogger(__name__)

def merge_entity_descriptions(descriptions_list):
    """ Merges multiple descriptions of entities with the same name, removing duplicates. """
    if not descriptions_list:
        return ""

    all_sentences = []
    for desc in descriptions_list:
        if desc and desc.strip():
            # Clean the description
            desc = desc.strip().rstrip(".")
            # Split into sentences
            sentences = re.split(r'[.!?]+', desc)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:  # Ignore very short fragments
                    all_sentences.append(sentence)
    
    # Remove duplicates
    seen = set()
    unique_sentences = []
    for sentence in all_sentences:
        # Normalize for comparison (lowercase, remove extra spaces)
        normalized = ' '.join(sentence.lower().split())
        if normalized not in seen and normalized:
            seen.add(normalized)
            unique_sentences.append(sentence)
    
    # Join sentences again
    if unique_sentences:
        return ". ".join(unique_sentences) + "."
    return ""

def extract_entities_and_relationships_from_chunks(chunks_url, llm: OllamaModel, max_chunks=None):
    """ Extracts entities and relationships from chunks, combining descriptions for duplicate entities and cleaning/validating relationships."""
    entity_dict = defaultdict(list)
    all_relationships = []
    
    # Limit chunks if specified (used for testing or on machines with limited resources). I tested it with 5 chunks max because of my machines capabilities
    chunks_to_process = chunks_url[:max_chunks] if max_chunks else chunks_url
    
    logger.info(f"Processing {len(chunks_to_process)} chunks for entity extraction")
    
    for i, chunk in enumerate(chunks_to_process, 1):
        logger.info(f"Processing chunk {i}/{len(chunks_to_process)}")
        
        try:
            entities_relationships_dict = llm.extract_knowledge_simultaneously(chunk.page_content)
            
            if not entities_relationships_dict:
                logger.warning(f"No entities or relationships extracted from chunk {i}")
                continue
            
            entities_dict = entities_relationships_dict.get("entities", {})
            relationships = entities_relationships_dict["relationships"]
                
            for name, description in entities_dict.items():  
                entity_dict[name].append(description.strip())
                    
                logger.info(f"Chunk {i} - Entity: {name}, Description: {description}")
            
            # Collect relationships
            if relationships:
                all_relationships.extend(relationships)
                logger.info(f"Chunk {i} - Extracted {len(relationships)} relationships")
                
        except Exception as e:
            logger.error(f"Error processing chunk {i}: {e}")
            continue
    
    # Combine descriptions for each entity
    final_entities = {}
    
    logger.info("*********** Combining entity descriptions ***********")
    
    for entity_name, descriptions in entity_dict.items():
        combined_description = merge_entity_descriptions(descriptions)
        
        if combined_description:
            final_entities[entity_name] = combined_description
            
            logger.info(f"Final Entity: {entity_name}")
            logger.info(f"Combined from {len(descriptions)} descriptions")
            logger.info(f"Description: {combined_description}")
            logger.info("-" * 80)
    
    logger.info("*********** Cleaning and validating relationships ***********")
    final_relationships = clean_and_validate_relationships(all_relationships)
    
    # Remove duplicate relationships
    unique_relationships = []
    seen_relationships = set()
    
    for rel in final_relationships:
        rel_key = (rel[0].lower(), rel[1].lower(), rel[2].lower())
        if rel_key not in seen_relationships:
            seen_relationships.add(rel_key)
            unique_relationships.append(rel)
    
    logger.info(f"Total unique entities: {len(final_entities)}")
    logger.info(f"Total unique relationships: {len(unique_relationships)}")
    logger.info(f"Relationships cleaned from {len(all_relationships)} to {len(unique_relationships)}")
    
    return {
        "entities": final_entities,
        "relationships": unique_relationships
    }
    
def clean_and_validate_relationships(relationships):
    """ Cleans and validates relationships by removing malformed ones: """
    cleaned_relationships = []
    
    for rel in relationships:
        try:
            # Make sure tuple has exactly 3 elements
            if not isinstance(rel, (tuple, list)) or len(rel) != 3:
                logger.warning(f"Skipping malformed relationship (not 3 elements): {rel}")
                continue
            
            subject, predicate, obj = rel
            
            # Skip if subject or object is None
            if subject is None or obj is None:
                logger.warning(f"Skipping relationship with None values: {rel}")
                continue
            
            # Convert to strings and strip whitespace
            subject = str(subject).strip() if subject is not None else ""
            predicate = str(predicate).strip() if predicate is not None else ""
            obj = str(obj).strip() if obj is not None else ""
            
            # Skip empty subject or object
            if not subject or not obj:
                logger.warning(f"Skipping relationship with empty subject or object: {rel}")
                continue
            
            cleaned_rel = (subject, predicate, obj)
            
            if cleaned_rel not in cleaned_relationships:
                cleaned_relationships.append(cleaned_rel)
                logger.info(f"Added relationship: {cleaned_rel}")
            
        except Exception as e:
            logger.error(f"Error processing relationship {rel}: {e}")
            continue
    
    return cleaned_relationships