import networkx as nx
from typing import Dict
import numpy as np

# Compute the Largest Connected Componenet (lcc) of a graph 
def compute_lcc(graph: nx.Graph) -> nx.Graph:
    
    # Convert directed graphs to undirected
    # Connectivity is defined in undirected sense for diffusion metrics
    if graph.is_directed():
        undirected_graph = graph.to_undirected()
    else:
        undirected_graph = graph
    
    # Edge case: empty graph
    if undirected_graph.number_of_nodes() == 0:
        return undirected_graph
    
    # If graph is already connected the return as-is
    if nx.is_connected(undirected_graph):
        return undirected_graph

    # Curate a list of all nodes adn the no. of connections they have
    sorted_connections = sorted(nx.connected_components(undirected_graph), key=len, reverse=True) 
    
    return undirected_graph.subgraph(sorted_connections[0]).copy()

def graph_metrics(graph: nx.Graph) -> Dict[str, float]:
    """
    Graph-level structural metrics oriented toward hub emergence and
    attention concentration (not SIR diffusion).
    """
    undirected_graph = graph.to_undirected() if graph.is_directed() else graph

    n = undirected_graph.number_of_nodes()
    m = undirected_graph.number_of_edges()

    if n == 0:
        return {}

    degrees = np.array([d for _, d in undirected_graph.degree()], dtype=float)

    avg_degree = float(degrees.mean()) if n > 0 else 0.0
    max_degree = float(degrees.max()) if n > 0 else 0.0

    # Degree inequality (hub dominance proxy)
    # Gini coefficient over degree distribution
    if avg_degree > 0:
        degree_gini = float(
            np.abs(degrees[:, None] - degrees).sum()
            / (2 * n * n * avg_degree)
        )
    else:
        degree_gini = 0.0

    # Hub share
    # Fraction of all edges incident to the top-k nodes
    k = max(1, int(0.01 * n))  # top 1%
    top_k_degrees = np.sort(degrees)[-k:]
    hub_edge_share = float(top_k_degrees.sum() / (2 * m)) if m > 0 else 0.0

    # Clustering (local reinforcement potential)
    avg_clustering = (
        float(nx.average_clustering(undirected_graph))
        if n > 2
        else 0.0
    )

    # Degree assortativity (rich-get-richer vs egalitarian growth)
    try:
        assortativity = (
            float(nx.degree_assortativity_coefficient(undirected_graph))
            if n > 2
            else float("nan")
        )
    except Exception:
        assortativity = float("nan")

    return {
        "nodes": float(n),
        "edges": float(m),
        "avg_degree": avg_degree,
        "max_degree": max_degree,
        "degree_gini": degree_gini,
        "top_1pct_edge_share": hub_edge_share,
        "avg_clustering": avg_clustering,
        "degree_assortativity": assortativity,
    }


    