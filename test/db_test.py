import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.vector_database import VectorDatabase
import pytest


db = VectorDatabase()

def test_init():
    assert db.vector_store is not None
    assert hasattr(db.vector_store, "add_documents")

def test_add_document_triplets():
    triple = ["triple 1", "triple 2", "Data"]
    triples = [
    ("Kylian Mbappé", "is close to joining", "Real Madrid"),
    ("Kylian Mbappé", "currently plays for", "Paris Saint-Germain"),
    ("Kylian Mbappé", "is regarded as", "one of the best forwards"),
    ("Real Madrid", "have pursued", "Kylian Mbappé for years"),
    ("Real Madrid", "offered", "record-breaking contract"),
    ("Contract offer", "includes", "performance-based bonuses")]

    source = "test_source"
    db.add_document_triplets(triples, source)

    docs = db.get_sources()
    print(f'Documents: {docs}')


    # There's no direct public method to fetch docs, so just test no error is raised
    # If your Chroma instance has a method to count or get docs, you can add checks here

def test_clear_database():
    # Add some documents first
    triples = ["t1", "t2", "t3"]
    source = "src"
    db.add_document_triplets(triples, source)

    before_clear = db.vector_store.get()    
    assert len(before_clear["documents"]) != 0

    # Clear the DB
    db.clear_database()

    after_clear = db.vector_store.get()
    assert len(after_clear["documents"]) == 0


