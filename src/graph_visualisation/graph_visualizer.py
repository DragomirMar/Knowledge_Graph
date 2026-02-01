import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from graph_visualisation.graph_state import get_graph_data
from graph_visualisation.graph_builder import get_nodes_and_edges_from_db
from graph_visualisation.graph_state import load_graph_into_session
   
import networkx as nx
import math

def create_agraph_elements(nodes, edges, selected=None, filter_out_isolated=False):
    nodes_list = []
    edges_list = []
    
    # Create NetworkX graph for layout calculation
    G = nx.DiGraph()
    for node_id in nodes.keys():
        G.add_node(node_id)
    for src, tgt, _ in edges:
        G.add_edge(src, tgt)
    
    # Calculate node importance (centrality)
    try:
        degree_centrality = nx.degree_centrality(G)
        pagerank = nx.pagerank(G)
        betweenness = nx.betweenness_centrality(G)
    except:
        degree_centrality = {node: 1 for node in G.nodes()}
        pagerank = {node: 1 for node in G.nodes()}
        betweenness = {node: 1 for node in G.nodes()}
    
    # Don't show isolated nodes if requested
    if filter_out_isolated:
        # Remove nodes with no connections from the nodes dict and from the graph
        nodes = {nid: props for nid, props in nodes.items() if G.degree(nid) > 0}
        isolated = [n for n in G.nodes() if G.degree(n) == 0]
        G.remove_nodes_from(isolated)
                
    # === CUSTOM LAYOUT ALGORITHM ===
    pos = {}
    
    # Get top hubs based on degree centrality
    num_hubs = min(7, max(3, len(G.nodes()) // 30))
    hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:num_hubs]
    hub_nodes = [node for node, _ in hubs]
    
    # Place hubs in a circle in the center
    hub_radius = 400
    for i, hub in enumerate(hub_nodes):
        angle = (2 * math.pi * i) / len(hub_nodes)
        pos[hub] = (hub_radius * math.cos(angle), hub_radius * math.sin(angle))
    
    placed = set(hub_nodes)
    
    # For each hub, place its direct connections around it
    spoke_radius = 600
    
    for hub in hub_nodes:
        neighbors = set(G.neighbors(hub)) | set(G.predecessors(hub))
        neighbors = [n for n in neighbors if n not in placed]
        
        if not neighbors:
            continue
        
        hub_x, hub_y = pos[hub]
        
        for i, neighbor in enumerate(neighbors):
            angle = (2 * math.pi * i) / len(neighbors)
            hub_angle = math.atan2(hub_y, hub_x)
            adjusted_angle = angle + hub_angle
            
            x = hub_x + spoke_radius * math.cos(adjusted_angle)
            y = hub_y + spoke_radius * math.sin(adjusted_angle)
            pos[neighbor] = (x, y)
            placed.add(neighbor)
    
    # For remaining nodes, place them as spokes of already-placed nodes
    remaining = [n for n in G.nodes() if n not in placed and G.degree(n) > 0]
    secondary_spoke_radius = 700
    
    while remaining:
        newly_placed = []
        
        for node in remaining:
            neighbors = set(G.neighbors(node)) | set(G.predecessors(node))
            placed_neighbors = [n for n in neighbors if n in placed]
            
            if placed_neighbors:
                anchor = placed_neighbors[0]
                anchor_x, anchor_y = pos[anchor]
                
                attached_count = sum(
                    1 for p_node, (px, py) in pos.items() 
                    if p_node != anchor and 
                    math.sqrt((px - anchor_x)**2 + (py - anchor_y)**2) < secondary_spoke_radius + 100
                )
                
                angle = (2 * math.pi * attached_count) / max(6, len(placed_neighbors))
                x = anchor_x + secondary_spoke_radius * math.cos(angle)
                y = anchor_y + secondary_spoke_radius * math.sin(angle)
                
                pos[node] = (x, y)
                newly_placed.append(node)
        
        if not newly_placed:
            for i, node in enumerate(remaining):
                hub = hub_nodes[i % len(hub_nodes)]
                hub_x, hub_y = pos[hub]
                angle = (2 * math.pi * i) / len(remaining)
                x = hub_x + (spoke_radius + secondary_spoke_radius) * math.cos(angle)
                y = hub_y + (spoke_radius + secondary_spoke_radius) * math.sin(angle)
                pos[node] = (x, y)
            break
        
        for node in newly_placed:
            remaining.remove(node)
            placed.add(node)
    
    main_graph_bounds = {
        'min_x': float('inf'),
        'max_x': float('-inf'),
        'min_y': float('inf'),
        'max_y': float('-inf')
    }
    
    if pos:
        for node_id, (x, y) in pos.items():
            main_graph_bounds['min_x'] = min(main_graph_bounds['min_x'], x)
            main_graph_bounds['max_x'] = max(main_graph_bounds['max_x'], x)
            main_graph_bounds['min_y'] = min(main_graph_bounds['min_y'], y)
            main_graph_bounds['max_y'] = max(main_graph_bounds['max_y'], y)
    else:
        # Fallback if no nodes placed yet
        main_graph_bounds = {'min_x': -1000, 'max_x': 1000, 'min_y': -1000, 'max_y': 1000}
    
    # Node categorization by connectivity
    low_connectivity_nodes = []  # Nodes with 1-2 connections, not in main component
    small_components = []  # Small isolated clusters (3-10 nodes)
    isolated_nodes = []  # No connections

    # Get connected components
    undirected_G = G.to_undirected()
    components = list(nx.connected_components(undirected_G))

    # Find main component (contains hubs)
    main_component = None
    for component in components:
        if any(hub in component for hub in hub_nodes):
            main_component = component
            break

    # Categorize remaining components
    for component in components:
        if component == main_component:
            continue  # Skip main component
        
        component_list = list(component)
        
        if len(component_list) == 1:
            node = component_list[0]
            if G.degree(node) == 0:
                isolated_nodes.append(node)
            else:
                low_connectivity_nodes.append(node)
        elif len(component_list) == 2: # 2-node components to low-connectivity grid
            low_connectivity_nodes.extend(component_list)
        elif 3 <= len(component_list) <= 10: # 3-10 node components to small components
            small_components.append(component_list)

    padding = 400  # Space between sections
    
    low_connectivity_height = 0
    if low_connectivity_nodes:
        grid_start_x = main_graph_bounds['max_x'] + padding
        grid_start_y = main_graph_bounds['max_y']  # Start at top of main graph
        node_spacing = 300
        nodes_per_row = 8
        
        for i, node in enumerate(low_connectivity_nodes):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            x = grid_start_x + (col * node_spacing)
            y = grid_start_y - (row * node_spacing)
            
            pos[node] = (x, y)
        
        # Calculate how much vertical space the grid used
        num_rows = (len(low_connectivity_nodes) + nodes_per_row - 1) // nodes_per_row
        low_connectivity_height = num_rows * node_spacing

    if small_components:
        component_start_x = main_graph_bounds['max_x'] + padding
        
        if low_connectivity_nodes:
            # Start below the low-connectivity grid
            component_start_y = main_graph_bounds['max_y'] - low_connectivity_height - padding
        else:
            component_start_y = main_graph_bounds['max_y'] # Start at top of main graph
        
        current_x = component_start_x
        current_y = component_start_y
        
        # Dynamic max width based on screen space
        max_width = component_start_x + 2000  # Allow 2000px width for component area
        row_height = 0
        
        for component in small_components:
            if len(component) == 0:
                continue
            
            # Find hub of this small component
            comp_hub = max(component, key=lambda n: G.degree(n))
            subG = G.subgraph(component)
            
            # Use compact circular layout for this component
            comp_distances = {}
            queue = [(comp_hub, 0)]
            visited = {comp_hub}
            
            while queue:
                node, dist = queue.pop(0)
                comp_distances[node] = dist
                
                neighbors = set(subG.neighbors(node)) | set(subG.predecessors(node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, dist + 1))
            
            # Group by distance
            comp_levels = {}
            for node, dist in comp_distances.items():
                if dist not in comp_levels:
                    comp_levels[dist] = []
                comp_levels[dist].append(node)
            
            # Place component hub
            pos[comp_hub] = (current_x, current_y)
            
            max_radius = 0
            for level, level_nodes in sorted(comp_levels.items()):
                if level == 0:
                    continue
                
                # Dynamic radius based on component structure
                base_radius = 200
                radius_increment = 150
                radius = base_radius + (level - 1) * radius_increment
                max_radius = max(max_radius, radius)
                num_nodes = len(level_nodes)
                
                if num_nodes > 0:
                    for i, node in enumerate(level_nodes):
                        angle = (2 * math.pi * i) / num_nodes
                        x = current_x + radius * math.cos(angle)
                        y = current_y + radius * math.sin(angle)
                        pos[node] = (x, y)
            
            # Update position for next component
            component_spacing = 350
            component_width = max(max_radius * 2 + component_spacing, 450)
            current_x += component_width
            row_height = max(row_height, max_radius * 2 if max_radius > 0 else 300)
            
            # Wrap to next row if needed
            if current_x > max_width:
                current_x = component_start_x
                current_y -= (row_height + component_spacing)
                row_height = 0
    
    if isolated_nodes: # Position below everything else
        # Find the lowest point used so far
        lowest_y = min(y for x, y in pos.values()) if pos else 0
        
        isolated_start_x = main_graph_bounds['max_x'] + padding
        isolated_start_y = lowest_y - padding 
        node_spacing = 170
        nodes_per_row = 10
        
        for i, node in enumerate(isolated_nodes):
            row = i // nodes_per_row
            col = i % nodes_per_row
            
            x = isolated_start_x + (col * node_spacing)
            y = isolated_start_y - (row * node_spacing)
            
            pos[node] = (x, y)
    
    # Calculate node sizes based on importance
    num_nodes = len(nodes)
    base_size = max(15, 25 - (num_nodes // 30))
    
    max_centrality = max(degree_centrality.values()) if degree_centrality else 1
    
    for node_id, props in nodes.items():
        x_pos, y_pos = pos.get(node_id, (0, 0))  # Fallback to origin if not positioned
        x_pos *= 1.0
        y_pos *= 1.0
        
        # Calculate size based on centrality
        importance = degree_centrality.get(node_id, 0)
        importance_multiplier = 1 + (importance / max_centrality) * 1.5
        
        # Different color for isolated nodes
        node_degree = G.degree(node_id)
        
        if node_id == selected:
            color = "#FFD700"
            font_color = "#FFFFFF"
            size = (base_size + 10) * importance_multiplier
        elif node_degree == 0:
            color = "#757575"
            font_color = "#FFFFFF"
            size = base_size + 10
        else:
            color = "#4FC3F7"
            font_color = "#FFFFFF" 
            size = base_size * importance_multiplier
        
        node = Node(
            id=node_id,
            label=props["label"],
            title=f"{props['label']}: {props['description']}\nConnections: {node_degree}",
            color=color,
            size=int(size),
            x=x_pos,
            y=y_pos,
            font={
                "color": font_color,
                "size": int(12 + importance_multiplier * 2),
                "face": "arial",
                "strokeWidth": 1,
                "strokeColor": "#D6B703" if node_id == selected else "#333333"
            }
        )
        nodes_list.append(node)
    
    # Edges
    for src, tgt, relation in edges:
        if src == selected or tgt == selected:
            edge_color = "#FFA500"
        else:
            edge_color = "#B0BEC5"
            
        edge = Edge(
            source=src,
            target=tgt,
            label=relation,
            type="CURVE_SMOOTH",
            color=edge_color, 
            font={
                "color": "#FFFFFF",  
                "size": 11,
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
    
    filter = st.checkbox("Filter out isolated nodes", value=False)
    
    st.markdown("### Interactive Knowledge Graph")
    st.markdown(f"Showing **{len(data['nodes'])}** entities and **{len(data['edges'])}** relationships")
    
    try:
        nodes, edges = create_agraph_elements(data["nodes"], data["edges"], selected=data["selected_node"], filter_out_isolated=filter)

        config = Config(
            width=2000,
            height=1200,
            directed=True,
            physics={
                "enabled": True, 
                "stabilization": {"enabled": False}, 
                "barnesHut": {
                    "gravitationalConstant": 0,
                    "centralGravity": 0,
                    "springConstant": 0,
                    "damping": 1
                }
            },
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#FFD700",
            node={
                'labelProperty': 'label',
                'fontSize': 14,
                'fontColor': '#FFFFFF', 
                'borderWidth': 2,
            },
            link={
                'labelProperty': 'label', 
                'renderLabel': True,
                'fontSize': 11,
                'fontColor': '#FFFFFF'
            },
            interaction={
                "dragNodes": True,
                "dragView": True,
                "zoomView": True,
                "hover": True,
                "navigationButtons": True,
                "zoomSpeed": 0.5
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
    
    # Categorize edges by direction
    incoming_nodes = set() 
    outgoing_nodes = set() 
    bidirectional_nodes = set()
    relevant_edges = []
    
    for src, tgt, relation in data["edges"]:
        if src == center_node_id:
            # Center node points to tgt (outgoing)
            if tgt in incoming_nodes:
                # Already have incoming edge, so it's bidirectional
                incoming_nodes.remove(tgt)
                bidirectional_nodes.add(tgt)
            elif tgt not in bidirectional_nodes:
                outgoing_nodes.add(tgt)
            relevant_edges.append((src, tgt, relation))
        elif tgt == center_node_id:
            # src points to center node (incoming)
            if src in outgoing_nodes:
                # Already have outgoing edge, so it's bidirectional
                outgoing_nodes.remove(src)
                bidirectional_nodes.add(src)
            elif src not in bidirectional_nodes:
                incoming_nodes.add(src)
            relevant_edges.append((src, tgt, relation))
    
    if not relevant_edges:
        st.info("No connections found for this entity")
        return
    
    try:
        pos = {}
        
        # Place center node at origin
        pos[center_node_id] = (0, 0)
        
        # Convert to lists for positioning
        incoming_list = list(incoming_nodes)
        outgoing_list = list(outgoing_nodes)
        bidirectional_list = list(bidirectional_nodes)
        
        # Layout parameters
        horizontal_distance = 500  # Distance from center horizontally
        vertical_spacing = 150     # Spacing between nodes vertically
        
        # Incoming nodes on the LEFT
        if incoming_list:
            start_y = -(len(incoming_list) - 1) * vertical_spacing / 2
            for i, node_id in enumerate(incoming_list):
                x = -horizontal_distance
                y = start_y + i * vertical_spacing
                pos[node_id] = (x, y)
        
        # Outgoing nodes on the RIGHT
        if outgoing_list:
            start_y = -(len(outgoing_list) - 1) * vertical_spacing / 2
            for i, node_id in enumerate(outgoing_list):
                x = horizontal_distance
                y = start_y + i * vertical_spacing
                pos[node_id] = (x, y)
        
        # Bidirectional nodes ABOVE (or you can split them left/right)
        if bidirectional_list:
            # Split bidirectional nodes: half left, half right
            half = len(bidirectional_list) // 2
            
            # Left half
            for i in range(half):
                x = -horizontal_distance
                y = (len(incoming_list) * vertical_spacing / 2) + (i + 1) * vertical_spacing
                pos[bidirectional_list[i]] = (x, y)
            
            # Right half
            for i in range(half, len(bidirectional_list)):
                x = horizontal_distance
                y = (len(outgoing_list) * vertical_spacing / 2) + (i - half + 1) * vertical_spacing
                pos[bidirectional_list[i]] = (x, y)
        
        # Create nodes with positions
        nodes_list = []
        connected_nodes = incoming_nodes | outgoing_nodes | bidirectional_nodes | {center_node_id}
        
        for node_id in connected_nodes:
            if node_id in data["nodes"]:
                props = data["nodes"][node_id]
                x_pos, y_pos = pos[node_id]
                
                if node_id == center_node_id:
                    color = "#FFD700"  # Center node
                    font_color = "#FFFFFF"
                    size = 40
                elif node_id in bidirectional_nodes:
                    color = "#9C27B0"  # Bidirectional
                    font_color = "#FFFFFF"
                    size = 28
                elif node_id in incoming_nodes:
                    color = "#4CAF50"  # Incoming
                    font_color = "#FFFFFF"
                    size = 25
                else:  
                    color = "#2196F3"  # Outgoing
                    font_color = "#FFFFFF"
                    size = 25
                
                node = Node(
                    id=node_id,
                    label=props["label"],
                    title=f"{props['label']}: {props['description']}",
                    color=color,
                    size=size,
                    x=x_pos,
                    y=y_pos,
                    font={
                        "color": font_color,
                        "size": 14,
                        "face": "arial",
                        "strokeWidth": 1,
                        "strokeColor": "#000000" if node_id == center_node_id else "#333333"
                    }
                )
                nodes_list.append(node)
        
        # Create edges with directional coloring
        edges_list = []
        for src, tgt, relation in relevant_edges:
            if src == center_node_id:
                edge_color = "#2196F3"  # Outgoing
            elif tgt == center_node_id:
                edge_color = "#4CAF50"  # Incoming
            else:
                edge_color = "#B0BEC5"  # Fallback
            
            edge = Edge(
                source=src,
                target=tgt,
                label=relation,
                type="CURVE_SMOOTH",
                color=edge_color,
                font={
                    "color": "#FFFFFF",
                    "size": 11,
                    "strokeWidth": 1,
                    "strokeColor": "#000000"
                }
            )
            edges_list.append(edge)
        
        config = Config(
            width=2000,
            height=1200,
            directed=True,
            physics={
                "enabled": False
            },
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#FFD700",
            node={
                'labelProperty': 'label',
                'fontSize': 14,
                'fontColor': '#FFFFFF', 
                'borderWidth': 2,
            },
            link={
                'labelProperty': 'label', 
                'renderLabel': True,
                'fontSize': 11,
                'fontColor': '#FFFFFF'
            },
            interaction={
                "dragNodes": True,
                "dragView": True,
                "zoomView": True,
                "hover": True,
                "navigationButtons": True,
                "zoomSpeed": 0.5
            }
        )
        
        # Display the mini graph with legend
        st.markdown(f"**Graph View** - Showing connections to *{center_entity_name}*")
        st.markdown("🟢 **Green**: Incoming relationships | 🔵 **Blue**: Outgoing relationships | 🟣 **Purple**: Bidirectional")
        
        agraph(nodes=nodes_list, edges=edges_list, config=config)
        
    except ImportError:
        st.info("Install streamlit-agraph to see graph visualization")
    except Exception as e:
        st.error(f"Error displaying mini graph: {e}")