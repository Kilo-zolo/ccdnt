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
    undirected_graph = graph.to_undirected() if graph.is_directed() else graph
    lcc = compute_lcc(undirected_graph)

    # number of edges connected to each node
    degrees = [degree for _, degree in undirected_graph.degree()]
    avg_degree = float(np.mean(degrees)) if degrees else 0.0

    # average number of clusters in the graph
    avg_cluster = nx.average_clustering(undirected_graph) if undirected_graph.number_of_nodes() > 2 else 0.0

    try:
        avg_short_path_len = nx.average_shortest_path_length(lcc) if lcc.number_of_nodes() > 2 else float("nan")
    except Exception:
        avg_short_path_len = float("nan")

    try:
        assortativity = nx.degree_assortativity_coefficient(undirected_graph) if undirected_graph.number_of_nodes() > 2 else float("nan")
    except Exception:
        assortativity = float("nan")

    return{
        "number of nodes": float(undirected_graph.number_of_nodes()),
        "number of links": float(undirected_graph.number_of_edges()),
        "average number of links per node": avg_degree,
        "average number of clusters in the graph": float(avg_cluster), 
        "average path length": float(avg_short_path_len),
        "assortativity": float(assortativity),
        "length of largest connected component": float(lcc.number_of_nodes())
    }


    