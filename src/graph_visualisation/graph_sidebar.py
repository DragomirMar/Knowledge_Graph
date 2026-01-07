import streamlit as st
from database.database_manager import DBManager as dbm
from collections import defaultdict, deque
from graph_visualisation.graph_state import get_graph_data

def show_node_editor():
    data = get_graph_data()
    
    if not data["nodes"]:
        st.sidebar.info("No nodes available. Upload some documents first.")
        return
    
    st.sidebar.markdown("### Node Editor")
    # Dropdown for node selection
    node_options = {"None": None}
    for node_id, props in data["nodes"].items():
        node_options[props['label']] = node_id  

    selected_label = st.sidebar.selectbox("Select node to edit:", list(node_options.keys()))
    node_id = node_options[selected_label]

    if node_id:
        data["selected_node"] = node_id
        render_node_editor(node_id)
    else:
        data["selected_node"] = None

def render_node_editor(node_id):
    data = get_graph_data()
    
    if node_id not in data["nodes"]:
        st.sidebar.error("Node not found")
        return
    
    node = data["nodes"][node_id]
    original_name = node.get("original_name", node["label"])
    
    st.sidebar.markdown(f"**Editing:** {node['label']}")
    
    with st.sidebar.form(f"edit_node_{node_id}"):
        new_label = st.text_input("Name", value=node["label"])
        new_description = st.text_area("Description", value=node["description"], height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            update_btn = st.form_submit_button("Update")
        with col2:
            view_btn = st.form_submit_button("View Details")
        
        if update_btn:
            try:
                # Update in database
                if new_label != node["label"]:
                    dbm.update_entity_name(original_name, new_label)
                if new_description != node["description"]:
                    dbm.update_entity_description(new_label, new_description)
                
                # Update local data
                node["label"] = new_label
                node["description"] = new_description
                node["original_name"] = new_label
                
                st.sidebar.success("Node updated!")
                st.rerun()
                
            except Exception as e:
                st.sidebar.error(f"Error updating node: {str(e)}")
        
        if view_btn:
            # Navigate to entity details
            st.session_state.selected_entity = original_name
            st.session_state.current_page = "entity_detail"
            st.rerun()
        
def find_connected_components( ):
    nodes = st.session_state.graph_data["nodes"]
    edges = st.session_state.graph_data["edges"]
    
    graph = defaultdict(list)
    for src, tgt, _ in edges:
        graph[src].append(tgt)
        graph[tgt].append(src)  # undirected for component grouping

    visited = set()
    components = []

    for node in nodes:
        if node not in visited:
            queue = deque([node])
            comp = set()
            while queue:
                current = queue.popleft()
                if current not in visited:
                    visited.add(current)
                    comp.add(current)
                    queue.extend(graph[current])
            components.append(comp)
    return components
            
def show_graph_statistics( ):
    data = get_graph_data()
    
    st.sidebar.markdown("### Graph Statistics")

    # First row: Nodes & Edges
    col1, col2 = st.sidebar.columns(2)
    col1.metric("Nodes", len(data["nodes"]))
    col2.metric("Edges", len(data["edges"]))

    if data["nodes"]:
        components = find_connected_components()
        
        # Second row: Connected Components & Largest Component
        col3, col4 = st.sidebar.columns(2)
        col3.metric("Connected Components", len(components))
        if components:
            largest_component_size = max(len(comp) for comp in components)
            col4.metric("Largest Component", largest_component_size)