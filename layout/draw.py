import networkx as nx 
from typing import Dict, Tuple, List, Optional
import plotly.graph_objects as go

def draw_edge(graph: nx.Graph, loc: Dict[int, Tuple[float, float]], max_edges: int = 6000) -> go.Scatter:
    
    edges = list(graph.edges())
    
    if len(edges) > max_edges:
        edges = edges[:max_edges]
    
    a, b = [], []
    for loc_a, loc_b in edges:
        a0, b0 = loc[loc_a]
        a1, b1 = loc[loc_b]
        a += [a0, a1, None]
        b += [b0, b1, None]
    
    return go.Scatter(
        x=a,
        y=b,
        mode="lines",
        hoverinfo="none",
        line=dict(width=0.5),
        name="edges"
    )

def draw_node(
        graph: nx.Graph,
        loc: Dict[int, Tuple[float, float]],
        colors: List[int],
        hover: Optional[List[str]] = None
) -> go.Scatter:
    nodes = list(graph.nodes())
    a = [loc[node][0] for node in nodes]
    b = [loc[node][1] for node in nodes]

    if hover is None:
        degrees = dict(graph.degree())
        hover = [f"node={node}<br>degree_distribution={degrees.get(node,0)}<br>state={colors[i]}" for i, node in enumerate(nodes)]
    
    return go.Scatter(
        x=a,
        y=b,
        mode="markers",
        hoverinfo="text",
        text=hover,
        marker=dict(
            size=7,
            color=colors,
            cmin=0,
            cmax=2,
            colorscale=[
                [0.00, "#bdbdbd"],  # S
                [0.50, "#e74c3c"],  # I
                [1.00, "#2c3e50"],  # R
            ],
            line=dict(width=0)
        ),
        name="nodes"
    )

def update_colors_per_frame(graph: nx.Graph, iterations: List[dict]) -> Tuple[List[go.Frame], List[int]]:
    nodes = list(graph.nodes())
    current_node_state = dict()
    colors = [0] * len(nodes)

    frames: List[go.Frame] = []

    for iteration in iterations:
        iter_no = int(iteration.get("iteration", len(frames)))
        delta = iteration.get("status", {}) or {}
        current_node_state.update(delta)

        # build colors
        colors = [int(current_node_state.get(node, 0)) for node in nodes]

        infected = sum(1 for color in colors if color == 1)
        removed = sum(1 for color in colors if color == 2)
        susceptible = len(colors) - infected - removed

        frames.append(
            go.Frame(
                name=str(iter_no),
                data=[go.Scatter(marker=dict(color=colors))], # only update node marker colors
                layout=go.Layout(title=f"Information Cascade Model - iteration {iter_no} | S={susceptible}, I={infected}, R={removed}")
            )
        )
    return frames, colors

        