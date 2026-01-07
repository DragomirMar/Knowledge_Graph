
from io import BytesIO
import logging
from services.extract_text import extract_from_url, extract_from_pdf
from llm import OllamaModel
import entity_manager as em
from database.database_manager import DBManager as dbm

logger = logging.getLogger(__name__)

def process_documents(uploaded_documents, uploaded_urls):
    llm = OllamaModel()
    all_chunks = []
    
    # Process PDFs
    for pdf_file in uploaded_documents:
        try:
            file_like = BytesIO(pdf_file.read())
            chunks = extract_from_pdf(file_like)
            all_chunks.extend(chunks)
            logger.info(f"Extracted {len(chunks)} chunks from {pdf_file.name}")
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")
            continue
    
    # Process URLs
    for url in uploaded_urls:
        try:
            chunks = extract_from_url(url)
            all_chunks.extend(chunks)
            logger.info(f"Extracted {len(chunks)} chunks from {url}")
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
            continue
    
    if not all_chunks:
        return 0,0
    
    # Extract entities and relationships
    entities_and_relationships = em.extract_entities_and_relationships_from_chunks(
        all_chunks, llm
    )
    
    # Store in database
    entities = entities_and_relationships["entities"]
    relationships = entities_and_relationships["relationships"]
    
    entity_count = 0
    relationship_count = 0
    
    for name, description in entities.items():
        try:
            dbm.create_entity(name, description)
            entity_count += 1
        except Exception as e:
            logger.warning(f"Error creating entity {name}: {str(e)}")
    
    for subject, predicate, obj in relationships:
        try:
            dbm.create_relationship(subject, predicate, obj)
            relationship_count += 1
        except Exception as e:
            logger.warning(f"Error creating relationship {subject}-{predicate}-{obj}: {str(e)}")
    
    return entity_count, relationship_count    