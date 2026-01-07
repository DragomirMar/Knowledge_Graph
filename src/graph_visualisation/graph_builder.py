from collections import defaultdict
from database.database_manager import DBManager as dbm
import hashlib

def generate_node_id( name):
    # First 3 chars + hash 
    hash_suffix = hashlib.md5(name.encode()).hexdigest()[:4]
    clean_name = "".join(c.lower() for c in name if c.isalnum())[:6]
    return f"{clean_name}_{hash_suffix}"

def get_nodes_and_edges_from_db():
    entities = dbm.get_all_entities()
    relationships = dbm.get_all_relationships()
    
    # Convert entities to nodes format
    nodes = {}
    for entity in entities:
        node_id = generate_node_id(entity['name'])
        nodes[node_id] = {
            "label": entity['name'],
            "description": entity['description'] or "No description available",
            "original_name": entity['name']
        }
    
    # Convert relationships to edges format, grouping multiple predicates between same entities
    edge_groups = defaultdict(list)

    for rel in relationships:
        src_id = generate_node_id(rel['subject'])
        tgt_id = generate_node_id(rel['object'])
        edge_groups[(src_id, tgt_id)].append(rel['predicate'])

    edges = []
    for (src_id, tgt_id), predicates in edge_groups.items():
        label = "\n".join(
                            f"{p}," if i < len(predicates) - 1 else p
                            for i, p in enumerate(predicates)   
                            ) 
        edges.append((src_id, tgt_id, label))
        
    return nodes, edges