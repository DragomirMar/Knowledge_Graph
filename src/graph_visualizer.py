import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from collections import defaultdict, deque
from database_manager import DBManager as dbm
import logging

logger = logging.getLogger(__name__)

class GraphVisualizer:
    def __init__(self):
        self.initialize_graph_data()
    
    def initialize_graph_data(self):
        if "graph_data" not in st.session_state:
            st.session_state.graph_data = {
                "nodes": {},
                "edges": [],
                "selected_node": None,
                "last_updated": None
            }
    
    def load_data_from_database(self):
        self.initialize_graph_data()   # ensure graph_data exists

        try:
            # Get all entities and relationships
            entities = dbm.get_all_entities()
            relationships = dbm.get_all_relationships()
            
            # Convert entities to nodes format
            nodes = {}
            for entity in entities:
                node_id = self._generate_node_id(entity['name'])
                nodes[node_id] = {
                    "label": entity['name'],
                    "description": entity['description'] or "No description available",
                    "original_name": entity['name']
                }
            
            # Convert relationships to edges format
            edges = []
            for rel in relationships:
                src_id = self._generate_node_id(rel['subject'])
                tgt_id = self._generate_node_id(rel['object'])
                edges.append((src_id, tgt_id, rel['predicate']))
            
            # Update session state
            st.session_state.graph_data.update({
                "nodes": nodes,
                "edges": edges,
                "last_updated": len(entities) + len(relationships)
            })
            
            return True, f"Loaded {len(entities)} entities and {len(relationships)} relationships"
            
        except Exception as e:
            logger.error(f"Error loading data from database: {str(e)}")
            return False, f"Error loading data: {str(e)}"
    
    def _generate_node_id(self, name):
        """Generate a consistent node ID from entity name"""
        # Simple approach: use first 3 chars + hash to avoid collisions
        import hashlib
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:4]
        clean_name = "".join(c.lower() for c in name if c.isalnum())[:6]
        return f"{clean_name}_{hash_suffix}"
    
    def find_connected_components(self):
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
    
    def create_agraph_elements(self, selected=None):
        """Create nodes and edges for streamlit-agraph"""
        data = st.session_state.graph_data
        nodes_list = []
        edges_list = []
        
        # Create nodes with better colors for dark mode
        for node_id, props in data["nodes"].items():
            if node_id == selected:
                color = "#FFD700"  # Node color
                font_color = "#FFFFFF"  # Text color
                size = 30
            else:
                color = "#4FC3F7" 
                font_color = "#FFFFFF" 
                size = 25
            
            node = Node(
                id=node_id,
                label=props["label"],
                title=f"{props['label']}: {props['description']}",
                color=color,
                size=size,
                font={
                    "color": font_color,
                    "size": 16,
                    "face": "arial",
                    "strokeWidth": 1,
                    "strokeColor": "#D6B703" if node_id == selected else "#333333"
                }
            )
            nodes_list.append(node)
        
        # Create edges with better visibility
        for src, tgt, relation in data["edges"]:
            edge = Edge(
                source=src,
                target=tgt,
                label=relation,
                type="CURVE_SMOOTH",
                color="#B0BEC5", 
                font={
                    "color": "#FFFFFF",  
                    "size": 12,
                    "strokeWidth": 1,
                    "strokeColor": "#000000"
                }
            )
            edges_list.append(edge)
        
        return nodes_list, edges_list
    
    def show_graph_statistics(self):
        # Ensure graph_data is initialized
        self.initialize_graph_data()
        data = st.session_state.graph_data
        
        st.sidebar.markdown("### Graph Statistics")

        # First row: Nodes & Edges
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Nodes", len(data["nodes"]))
        col2.metric("Edges", len(data["edges"]))

        if data["nodes"]:
            components = self.find_connected_components()
            
            # Second row: Connected Components & Largest Component
            col3, col4 = st.sidebar.columns(2)
            col3.metric("Connected Components", len(components))
            if components:
                largest_component_size = max(len(comp) for comp in components)
                col4.metric("Largest Component", largest_component_size)
  
    def show_node_editor(self):
        """Show node editor in sidebar"""
        self.initialize_graph_data()
        data = st.session_state.graph_data
        
        if not data["nodes"]:
            st.sidebar.info("No nodes available. Upload some documents first.")
            return
        
        st.sidebar.markdown("### Node Editor")
        # Create a dropdown to select nodes
        node_options = {"None": None}
        for node_id, props in data["nodes"].items():
            node_options[props['label']] = node_id   # label → id map

        selected_label = st.sidebar.selectbox("Select node to edit:", list(node_options.keys()))
        node_id = node_options[selected_label]

        if node_id:
            data["selected_node"] = node_id
            self.render_node_editor(node_id)
        else:
            data["selected_node"] = None
    
    def render_node_editor(self, node_id):
        """Render the node editing form"""
        data = st.session_state.graph_data
        
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
    
    def render_graph(self):
        """Render the main graph visualization"""
        # Ensure graph_data is initialized
        self.initialize_graph_data()
        data = st.session_state.graph_data
        
        if not data["nodes"]:
            st.info("No data to visualize. Upload some documents first to see your knowledge graph!")
            return
        
        st.markdown("### Interactive Knowledge Graph")
        st.markdown(f"Showing **{len(data['nodes'])}** entities and **{len(data['edges'])}** relationships")
        
        try:
            nodes, edges = self.create_agraph_elements(selected=data["selected_node"])
            
            config = Config(
                width=1400, 
                height=800,  
                directed=True,
                physics={
                    "enabled": True,
                    "stabilization": {"enabled": True, "iterations": 100},
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 95,
                        "springConstant": 0.04,
                        "damping": 0.09
                    },
                    "maxVelocity": 20,
                    "minVelocity": 0.1,
                    "solver": "barnesHut",
                    "timestep": 0.35
                },
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#FFD700",
                collapsible=False,
                node={
                    'labelProperty': 'label',
                    'fontSize': 16,
                    'fontColor': '#FFFFFF', 
                    'borderWidth': 2,
                    'borderWidthSelected': 3
                },
                link={
                    'labelProperty': 'label', 
                    'renderLabel': True,
                    'fontSize': 12,
                    'fontColor': '#FFFFFF'  
                },
                interaction={
                    "dragNodes": True,
                    "dragView": True,
                    "hideEdgesOnDrag": False,
                    "hideNodesOnDrag": False,
                    "hover": True,
                    "hoverConnectedEdges": True,
                    "keyboard": {
                        "enabled": False
                    },
                    "multiselect": False,
                    "navigationButtons": True,
                    "selectable": True,
                    "selectConnectedEdges": True,
                    "tooltipDelay": 300,
                    "zoomView": True
                }
            )
            
            # Display the graph
            return_value = agraph(nodes=nodes, edges=edges, config=config)
            
            # Handle node selection from graph clicks
            if return_value:
                data["selected_node"] = return_value
                st.rerun()
            
        except ImportError:
            st.error("⚠️ **Missing Dependency**: Please install streamlit-agraph:")
            st.code("pip install streamlit-agraph")
        except Exception as e:
            st.error(f"Error displaying graph: {e}")
            st.info("Make sure streamlit-agraph is properly installed.")
    
    def render_mini_graph(self, center_entity_name, height=400):  
        """Render a smaller graph view focused on a specific entity"""
        self.initialize_graph_data()
        
        # Load data if not available
        if not st.session_state.graph_data["nodes"]:
            success, _ = self.load_data_from_database()
            if not success:
                st.info("Could not load graph data")
                return
        
        data = st.session_state.graph_data
        
        # Find the node ID for the center entity
        center_node_id = None
        for node_id, props in data["nodes"].items():
            if props["original_name"] == center_entity_name:
                center_node_id = node_id
                break
        
        if not center_node_id:
            st.info(f"Entity '{center_entity_name}' not found in graph")
            return
        
        # Get connected nodes (1-hop neighborhood)
        connected_nodes = {center_node_id}
        relevant_edges = []
        
        for src, tgt, relation in data["edges"]:
            if src == center_node_id or tgt == center_node_id:
                connected_nodes.add(src)
                connected_nodes.add(tgt)
                relevant_edges.append((src, tgt, relation))
        
        if not relevant_edges:
            st.info("No connections found for this entity")
            return
        
        try:
            # Create nodes (only connected ones) with better colors
            nodes_list = []
            for node_id in connected_nodes:
                if node_id in data["nodes"]:
                    props = data["nodes"][node_id]
                    if node_id == center_node_id:
                        color = "#FFD700"  # Gold for center
                        font_color = "#FFFFFF"
                        size = 35
                    else:
                        color = "#4FC3F7"  # Light blue
                        font_color = "#FFFFFF"
                        size = 25
                    
                    node = Node(
                        id=node_id,
                        label=props["label"],
                        title=f"{props['label']}: {props['description']}",
                        color=color,
                        size=size,
                        font={
                            "color": font_color,
                            "size": 14,
                            "face": "arial",
                            "strokeWidth": 1,
                            "strokeColor": "#000000" if node_id == center_node_id else "#333333"
                        }
                    )
                    nodes_list.append(node)
            
            # Create edges (only relevant ones)
            edges_list = []
            for src, tgt, relation in relevant_edges:
                edge = Edge(
                    source=src,
                    target=tgt,
                    label=relation,
                    type="CURVE_SMOOTH",
                    color="#B0BEC5",
                    font={
                        "color": "#FFFFFF",
                        "size": 10,
                        "strokeWidth": 1,
                        "strokeColor": "#000000"
                    }
                )
                edges_list.append(edge)
            
            # Configure the mini graph with better physics
            config = Config(
                width=800,  # Increased width
                height=height,
                directed=True,
                physics={
                    "enabled": True,
                    "stabilization": {"enabled": True, "iterations": 50},
                    "barnesHut": {
                        "gravitationalConstant": -4000,
                        "centralGravity": 0.2,
                        "springLength": 80,
                        "springConstant": 0.03,
                        "damping": 0.1
                    },
                    "maxVelocity": 15,
                    "minVelocity": 0.1,
                    "solver": "barnesHut"
                },
                hierarchical=False,
                nodeHighlightBehavior=True,
                highlightColor="#FFD700",
                collapsible=False,
                node={
                    'labelProperty': 'label',
                    'fontSize': 14,
                    'fontColor': '#FFFFFF'
                },
                link={
                    'labelProperty': 'label', 
                    'renderLabel': True,
                    'fontSize': 10,
                    'fontColor': '#FFFFFF'
                },
                interaction={
                    "dragNodes": True,
                    "dragView": True,
                    "hideEdgesOnDrag": False,
                    "hideNodesOnDrag": False,
                    "hover": True,
                    "navigationButtons": True,
                    "zoomView": True
                }
            )
            
            # Display the mini graph
            st.markdown(f"**Graph View** - Showing connections to *{center_entity_name}*")
            return_value = agraph(nodes=nodes_list, edges=edges_list, config=config)
            
            # Handle clicks - navigate to full graph view
            if return_value and return_value != center_node_id:
                clicked_entity = data["nodes"][return_value]["original_name"]
                st.info(f"Click 'View Full Graph' to explore {clicked_entity}")
            
        except ImportError:
            st.info("Install streamlit-agraph to see graph visualization")
        except Exception as e:
            st.error(f"Error displaying mini graph: {e}")
    
    def show_refresh_controls(self):
        """Show controls to refresh data from database"""
        # Ensure graph_data is initialized
        self.initialize_graph_data()
        
        st.markdown("### Graph Controls")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Data", type="primary"):
                success, message = self.load_data_from_database()
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with col2:
            if st.button("🎯 Reset View"):
                st.session_state.graph_data["selected_node"] = None
                st.rerun()

# Initialize graph visualizer
@st.cache_resource
def get_graph_visualizer():
    return GraphVisualizer()