from services.extract_text import *
from llm import OllamaModel
import logging
import database.database as db
from configuration.logger_config import setup_logging
import entity_manager as em
from database.database_manager import DBManager as dbm

"""A Class testing the functionality of the Knowledge Graph application without the streamlit interface."""

setup_logging()

logger = logging.getLogger(__name__)

logger.info('================ Starting script ================')
# Test Data
url = 'https://www.90min.com/why-liverpool-could-still-receive-trent-alexander-arnold-transfer-fee'
url1 = 'https://www.formula1.com/en/latest/article/piastri-storms-to-controlled-victory-in-bahrain-grand-prix-ahead-of-russell.47YQh0Ex2gkZcx58fRaRqJ'
url2 = 'https://www.tandfonline.com/doi/abs/10.1080/0264041031000102105'

# # PDF
# pdf_file_path = '../data/Formula.pdf'
# with open(pdf_file_path, 'rb') as f:
#     file_like = BytesIO(f.read())

logger.info("*********** Extract chunks ***********")

# 1. Extract and chunk text from a URL
chunks_url = extract_from_url(url)
logger.info(f"Number of chunks extracted from URL: {len(chunks_url)}")

for i,chunk in enumerate(chunks_url, start=1):
    logger.info(f"Chunk {i}: {chunk.page_content}")

logger.info("*********** Extract entities and relationships ***********")
llm = OllamaModel()

# 2. Extract entities and relationships together
final_entities = em.extract_entities_and_relationships_from_chunks(chunks_url, llm, max_chunks=5)

logger.info("*********** Store entities in database ***********")
# # 3. Store entities in a database
entities = final_entities["entities"]
relationships = final_entities["relationships"]

for name, description in entities.items():
    entity_id = dbm.create_entity(name, description)
    logger.info(f"Entity stored with ID: {entity_id}")
    
for subject, predicate, object in relationships:    
    relationship_id = dbm.create_relationship(subject, predicate, object)
    logger.info(f"Relationship stored with ID: {relationship_id}")
    
logger.info('================ End script ================')