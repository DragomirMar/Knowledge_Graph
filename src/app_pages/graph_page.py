import streamlit as st
from graph_visualisation.graph_visualizer import render_graph
from graph_visualisation.graph_sidebar import show_node_editor, show_graph_statistics
from graph_visualisation.graph_builder import get_nodes_and_edges_from_db
from graph_visualisation.graph_state import load_graph_into_session

def render_page():
    st.title("📊 Knowledge Graph Visualization")
    
    # Load data from database on first visit or when requested
    if not st.session_state.get('graph_data', {}).get('nodes'):
        with st.spinner("Loading graph data from database..."):
            nodes, edges = get_nodes_and_edges_from_db()
            success, message = load_graph_into_session(nodes, edges)
            if success:
                st.success(message)
            else:
                st.error(message)
    
    st.markdown("---")
    st.markdown("### Graph Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", type="primary"):
            nodes, edges = get_nodes_and_edges_from_db()
            success, message = load_graph_into_session(nodes, edges)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        if st.button("🎯 Reset View"):
            st.session_state.graph_data["selected_node"] = None
            st.rerun()
            
    render_graph()
    
    # Show sidebar options
    with st.sidebar:
        show_graph_statistics()
        st.markdown("---")
        show_node_editor()