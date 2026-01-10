from dataclasses import dataclass

@dataclass
class NetTopologyConfig:
    name: str
    nodes: int
    seed: int = 25

    # Erdos-Renyi
    node_birth_probability: float = 0.01
    directed: bool = False

    # Watts-Strogatz
    no_linked_nodes: int = 10
    stage_relink_probability: float = 0.1

    # Barbasi-Albert
    no_linked_edges: int = 3

    # Holme-Kim
    tri_formation_probability: float = 0.3

@dataclass
class CascadeConfig:
    fraction_infected: float = 0.01
    influence_probability: float = 0.05
    activity_rate: float = 2.5
    base_influence: float = 0.05
    preferential_amplification: float = 0.02
    iterations: int = 60
    seed: int = 25

DEFAULT_NET_TOPOLOGIES = {
    "Erdos-Renyi": NetTopologyConfig(name="ER", nodes=1200, node_birth_probability=0.004, directed=False),
    "Watts-Strogatz": NetTopologyConfig(name="WS", nodes=1200, no_linked_nodes=12, stage_relink_probability=0.12),
    "Barbasi-Albert": NetTopologyConfig(name="BA", nodes=1200, no_linked_edges=3),
    "Holme-Kim": NetTopologyConfig(name="HK", nodes=1200, no_linked_edges=3, tri_formation_probability=0.3)
}

