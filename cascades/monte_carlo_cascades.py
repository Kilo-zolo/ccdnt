import networkx as nx
import numpy as np
from config import CascadeConfig
from cascades.custom_cascades import run_custom_cascade
from cascades.timeseries_cascades import cascade_timeseries

def cascade_size_monte_carlo(
        graph: nx.Graph,
        config: CascadeConfig,
        runs: int = 25
) -> np.ndarray:
    sizes = []
    base_seed = config.seed

    for run in range(runs):
        cascade_information = CascadeConfig(
            fraction_infected=config.fraction_infected,
            influence_probability=config.influence_probability,
            iterations=config.iterations,
            seed=base_seed + run * 17 
        )
        init_cascade = run_custom_cascade(graph, cascade_information)
        init_timeseries = cascade_timeseries(init_cascade, graph.number_of_nodes())
        sizes.append(float(init_timeseries["total_infected"].iloc[-1]))
    return np.array(sizes, dtype=float)
