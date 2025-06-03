from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Tuple
from uuid import uuid4
from collections import defaultdict

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
)

class VectorDatabase:
    
    def __init__(self):   
        self.vector_store = Chroma(
            collection_name="my_collection",
            embedding_function=embeddings,   
        )
        
        
    def get_all_triplets_by_source(self):
        # Access the underlying ChromaDB collection
        results = self.vector_store.get()
        documents_only = results['documents']
        parsed_triplets = [tuple(entry.split(" | ")) for entry in documents_only]

        print(f'get_all_triplets_by_source results {parsed_triplets}')
        
        return parsed_triplets
    
    
    def add_document_triplets(self, triples, source):
        print(f'''add_document_triplets params
        {source}
        {triples}
        ''')

        documents = [Document(page_content=' | '.join(triplet), metadata={"source":source}, id=idx) for idx, triplet in enumerate(triples)]
        
        print(f'add_document_triplets docs {documents}')
        # print(f'add_document_triplets embeds {embeddings.embed_query("Test triple")}')
        
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)

    def clear_database(self):
        self.vector_store.reset_collection()
    
    def similarity_search(self, query: str, k: int = 5) -> List[str]:
        results = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in results]

    def get_sources(self):
        all_data = self.vector_store.get(include=["metadatas"])

        sources = set()
        for metadata in all_data["metadatas"]:
            source = metadata.get("source")
            if source:
                sources.add(source)
            else:
                sources.add("unknown source")
        return sources if sources else ["DATABASE IS EMPTY!"]