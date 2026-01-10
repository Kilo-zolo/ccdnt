from config import NetTopologyConfig
import networkx as nx

def build_graph(ntconfig: NetTopologyConfig) -> nx.Graph:
    set_seed = ntconfig.seed


    if ntconfig.name == "ER":
        graph = nx.erdos_renyi_graph(ntconfig.nodes, ntconfig.node_birth_probability, seed=set_seed, directed=ntconfig.directed)
        if ntconfig.directed:
            pass
        return graph
    
    if ntconfig.name == "WS":
        links = int(ntconfig.no_linked_nodes)
        
        # links need to be even
        # due to large clustering in this model the nodes need to be evenly connected
        # in a lattice like struct
        if links % 2 == 1:
            links += 1
        node_links = max(2, min(links, ntconfig.nodes - 1))
        graph = nx.watts_strogatz_graph(ntconfig.nodes, node_links, ntconfig.stage_relink_probability, seed=set_seed)
        return graph
    
    if ntconfig.name == "BA":
        edge_links = max(1, min(int(ntconfig.no_linked_edges), ntconfig.nodes - 1))
        graph = nx.barabasi_albert_graph(ntconfig.nodes, edge_links, seed=set_seed)
        return graph 
    
    if ntconfig.name == "HK":
        edge_links = max(1, min(int(ntconfig.no_linked_edges), ntconfig.nodes - 1))
        tri_formation_probability = float(ntconfig.tri_formation_probability)
        graph = nx.powerlaw_cluster_graph(ntconfig.nodes, edge_links, tri_formation_probability, seed=set_seed)
        return graph

    raise ValueError(f"Unknown topology: {ntconfig.name}")

        


