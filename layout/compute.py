import networkx as nx
from typing import Dict, Tuple
from config import NetTopologyConfig

def compute_layout(graph: nx.Graph, seed: int = NetTopologyConfig.seed) -> Dict[int, Tuple[float, float]]:
    return nx.spring_layout(graph, seed=seed, k=None, iterations=50)
 