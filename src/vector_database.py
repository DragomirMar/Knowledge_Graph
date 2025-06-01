from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Tuple
from uuid import uuid4

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
)

class VectorDatabase:
    
    def __init__(self):   
        self.vector_store = Chroma(
            collection_name="my_collection",
            embedding_function=embeddings,   
        )
    
    def add_document_triplets(self, triples, source):
        print(f'''add_document_triplets params
        {source}
        {triples}
        ''')

        documents = [Document(page_content=' '.join(triplet), metadata={"source":source}, id=idx) for idx, triplet in enumerate(triples)]
        
        print(f'add_document_triplets docs {documents}')
        # print(f'add_document_triplets embeds {embeddings.embed_query("Test triple")}')
        
        uuids = [str(uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)

    def clear_database(self):
        self.vector_store.reset_collection()

    # def get_triplets(self):
    #     all_data = self.vector_store.get(include=["documents"])
 
    #     # Extract triplets from documents
    #     triplets = []
    #     for document in all_data["documents"]:
    #         triplets.append(document.page_content)
    #     #     triplet = document.page_content.split(' ', 2)  # Split into subject, predicate, object
    #     #     if len(triplet) == 3:
    #     #         triplets.append(tuple(triplet))
    #     #     else:
    #     #         triplets.append(("incomplete", "triplet", "data"))

    #     # return triplets if triplets else ["database is empty"]

    # def get_all_triples(self) -> List[Tuple[str, str, str]]:
    #     docs = self.vector_store.get(include=["documents", "metadatas"])
    #     triples = []
    #     for doc in docs["documents"]:
    #         parts = doc.split(" ", 2)  # splits into [subject, relation, object]
    #         if len(parts) == 3:
    #             triples.append(tuple(parts))
    #     return triples

    def get_sources(self):
        all_data = self.vector_store.get(include=["metadatas"])

        # Extract sources from metadata
        sources = set()
        for metadata in all_data["metadatas"]:
            source = metadata.get("source")
            if source:
                sources.add(source)
            else:
                sources.add("unknown source")

        return sources if sources else ["database is empty"]