import streamlit as st

def ensure_graph_state():
    if "graph_data" not in st.session_state:
            st.session_state.graph_data = {
                "nodes": {},
                "edges": [],
                "selected_node": None,
                "last_updated": None
            }

def get_graph_data():
    ensure_graph_state()
    return st.session_state.graph_data

def load_graph_into_session(nodes, edges):
    data = get_graph_data()
    
    try:
        # Update session state
        data.update({
            "nodes": nodes,
            "edges": edges,
            "last_updated": len(nodes) + len(edges)
        })

        return True, f"Loaded {len(nodes)} entities and {len(edges)} relationships"

    except Exception as e:
        return False, f"Error loading data: {str(e)}"