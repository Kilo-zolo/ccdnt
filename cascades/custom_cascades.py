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

    # choose nodes at random to attempt to infect neighbors
    nodes = list(graph.nodes())
    initial_count = int(len(nodes) * cascade.fraction_infected)
    active_nodes = set(np.random.choice(nodes, size=initial_count, replace=False))
    
    # var to store all iters node statuses and info
    history: List[dict] = []

    for iteration in range(cascade.iterations):
        activated_nodes = set(active_nodes)
        newly_infected: set[int] = set()

        for node in active_nodes:
            # node activity chance
            activity_strength = graph.nodes[node].get("activity", 0.0)
            
            # if rng roll has a higher rate than activity strength, node does not attempt to influence
            if random.random() > activity_strength:
                continue

            # get initial influence strength of node
            influence_strength = graph.nodes[node].get("influence", 0.0)

            # attempt to infect neighbors that have not already been activated
            for neighbour in graph.neighbors(node):
                if neighbour in activated_nodes:
                    continue
                
                # add weight to each edge (difficulty of infecting neighbors)
                edge_weight = float(graph.edges[node, neighbour].get("weight", 1.0))
                
                # probability to infect neighbors
                infection_probability = influence_strength * edge_weight

                # stochastic influence - if rng roll is less than p, neighbour is influenced
                if random.random() < infection_probability:
                    activated_nodes.add(neighbour)
                    newly_infected.add(neighbour)
        
        # preferential amplification - incrementaly increase the influence strength of node
        for node in newly_infected:
            graph.nodes[node]["influence"] *= (1 + CascadeConfig.preferential_amplification)

        # record history
        node_status = {node: 1 for node in activated_nodes} # 1 = active
        history.append({
            "iteration": iteration,
            "status": node_status
        })
        active_nodes = activated_nodes
    
    return history




                