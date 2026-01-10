from typing import List, Dict
import pandas as pd

def cascade_timeseries(iterations: List[dict], nodes: int) -> pd.DataFrame:
    
    current_node_state: Dict[int, int] = {}
    infected_counts = []
    iteration_number = []

    # In the Cascading model, status codes typically: 0 susceptible, 1 infected, 2 removed (depending on model)
    # We'll treat "infected" as state == 1, and count how many ever became infected or removed.
    ever_infected: set[int] = set()

    for iteration in iterations:
        iter_num = int(iteration.get("iteration", len(iteration_number)))
        
        # information on state of nodes within the specific iteration
        iteration_state = iteration.get("status", {}) or {}

        for node, state in iteration_state.items():
            current_node_state[node] = state
            if state in (1, 2):
                ever_infected.add(node)
        
        iteration_number.append(iter_num)
        infected_counts.append(len(ever_infected))
    
    # Metrics to compute and display
    
    # iteration value and total infected up to that iteration
    df = pd.DataFrame({"iter": iteration_number, "total_infected": infected_counts})
    
    # fraction of total infected over all nodes
    df["proportion_infected"] = df["total_infected"] / max(1, nodes)
    
    # nodes infected within this iteration
    df["recently_infected"] = df["total_infected"].diff().fillna(df["total_infected"])
    
    return df