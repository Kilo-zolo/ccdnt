from typing import List, Dict
import pandas as pd

def cascade_timeseries(iterations: List[dict], nodes: int) -> pd.DataFrame:
    
    rows = []


    # Count nodes that ever reacted or broadcasted
    total_reach: set[int] = set()

    for iteration in iterations:
        iter_num = int(iteration.get("iteration"))
        impacts = iteration.get("broadcaster_impacts", {}) or {}

        if impacts:
            values = list(impacts.values())
            rows.append({
                "iteration_number": iter_num,
                "number_of_broadcasters": len(values),
                "mean_responses": sum(values) / len(values),
                "max_responses": max(values),
                "standard_deviation": pd.Series(values).std(ddof=0),
                "total_responses": sum(values)
            })
        else:
            rows.append({
                "iteration_number": iter_num,
                "number_of_broadcasters": 0,
                "mean_responses": 0,
                "max_responses": 0,
                "standard_deviation": 0,
                "total_responses": 0
            })
    df = pd.DataFrame(rows)
    
    return df