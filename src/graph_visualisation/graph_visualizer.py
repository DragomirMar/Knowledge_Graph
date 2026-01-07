import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from graph_visualisation.graph_state import get_graph_data
from graph_visualisation.graph_builder import get_nodes_and_edges_from_db
from graph_visualisation.graph_state import load_graph_into_session

def create_agraph_elements(nodes, edges, selected=None):
    nodes_list = []
    edges_list = []
    
    # Nodes
    for node_id, props in nodes.items():
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
    
    # Edges
    for src, tgt, relation in edges:
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

def render_graph():
    data = get_graph_data()

    if not data["nodes"]:
        st.info("No data to visualize. Upload some documents first to see your knowledge graph!")
        return
    
    st.markdown("### Interactive Knowledge Graph")
    st.markdown(f"Showing **{len(data['nodes'])}** entities and **{len(data['edges'])}** relationships")
    
    try:
        nodes, edges = create_agraph_elements(data["nodes"], data["edges"], selected=data["selected_node"])

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
        
        # Node selection from graph clicks
        if return_value:
            data["selected_node"] = return_value
            st.rerun()
        
    except ImportError:
        st.error("⚠️ **Missing Dependency**: Please install streamlit-agraph:")
        st.code("pip install streamlit-agraph")
    except Exception as e:
        st.error(f"Error displaying graph: {e}")
        st.info("Make sure streamlit-agraph is properly installed.")

def render_mini_graph(center_entity_name):  
    """Render a smaller graph view focused on a specific entity"""
    data = get_graph_data()
    
    if not data["nodes"]:
        nodes, edges = get_nodes_and_edges_from_db()
        success, _ = load_graph_into_session(nodes, edges)
        if not success:
            st.info("Could not load graph data")
            return
    
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
        # Create nodes connected to the center node
        nodes_list = []
        for node_id in connected_nodes:
            if node_id in data["nodes"]:
                props = data["nodes"][node_id]
                if node_id == center_node_id:
                    color = "#FFD700"  # Main node
                    font_color = "#FFFFFF"
                    size = 35
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
                        "size": 14,
                        "face": "arial",
                        "strokeWidth": 1,
                        "strokeColor": "#000000" if node_id == center_node_id else "#333333"
                    }
                )
                nodes_list.append(node)
        
        # Create edges connected to the center node
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
        
        config = Config(
            width=800,
            height=400,
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