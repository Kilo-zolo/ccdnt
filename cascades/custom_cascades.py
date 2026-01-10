import networkx as nx
import numpy as np
from typing import List
import random
from config import CascadeConfig

def run_custom_cascade(
        graph: nx.Graph, cascade: CascadeConfig
        ) -> List[dict]:
    random.seed(cascade.seed)
    np.random.seed(cascade.seed)

    idle, broadcasting, reacting = 0, 1, 2

    nodes = list(graph.nodes())

    # set no. of initial influencers in system
    initial_influencer_count = max(1, int(len(nodes) * cascade.fraction_infected))

    # choose broadcasting nodes at random
    broadcasting_nodes = set(np.random.choice(nodes, size=initial_influencer_count, replace=False))

    # baseline state of all nodes
    base_node_state = {node: idle for node in nodes}
    
    # var to store all iters node statuses and info
    history: List[dict] = []

    for iteration in range(cascade.iterations):
        new_broadcasters: set[int] = set()
        reacting_nodes: set[int] = set()
        active_edges = set()
        broadcaster_impacts = {}
        
        for node in nodes:
            # decay BOTH reacting and broadcasting back to idle each tick
            if base_node_state[node] in (broadcasting, reacting):
                base_node_state[node] = idle

        for node in broadcasting_nodes:
            base_node_state[node] = broadcasting
            broadcaster_impacts[node] = 0

            activity = graph.nodes[node].get("activity", 0.0)
            influence = graph.nodes[node].get("influence", 0.0)

            if random.random() > activity:
                continue
            
            for neighbor in graph.neighbors(node):
                
                # local attention horizon, caps nodes from being attached to entire network
                if random.random() < influence:
                    reacting_nodes.add(neighbor)
                    broadcaster_impacts[node] += 1
                    active_edges.add((node, neighbor))
                
                    # promote to broadcaster only if node reacts
                    if random.random() < 0.15:
                        new_broadcasters.add(neighbor)
        
        for node in reacting_nodes:
            if base_node_state[node] != broadcasting:
                base_node_state[node] = reacting
            
        # broadcasters decay after info burst
        broadcasting_nodes = (new_broadcasters | {n for n in broadcasting_nodes if random.random() < 0.4})
        if not broadcasting_nodes:
            broadcasting_nodes = set(np.random.choice(nodes, size=initial_influencer_count, replace=False))

        
        # record snapshot
        node_status = base_node_state.copy()

        history.append({
            "iteration": iteration,
            "status": node_status,
            "broadcaster_impacts": broadcaster_impacts,
            "active_edges": list(active_edges)
        })
    
    return history




                