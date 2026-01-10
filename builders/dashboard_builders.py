from typing import Tuple, Dict
import numpy as np
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import NetTopologyConfig, CascadeConfig
from builders.graph_builders import build_graph
from builders.metric_builders import graph_metrics
from layout.compute import compute_layout
from layout.draw import draw_node, draw_edge, update_colors_per_frame  
from cascades.custom_cascades import run_custom_cascade
from cascades.monte_carlo_cascades import cascade_size_monte_carlo
from cascades.timeseries_cascades import cascade_timeseries

def build_dashboard(
        net_topology_label: str,
        net_topology_config: NetTopologyConfig,
        cascade_config: CascadeConfig, 
        runs: int
) -> Tuple[go.Figure, Dict[str, float]]:
    
    graph = build_graph(net_topology_config)

    for node in graph.nodes():
        graph.nodes[node]["activity"] = cascade_config.activity_rate
        graph.nodes[node]["influence"] = cascade_config.influence_probability

    metrics = graph_metrics(graph)

    # layout
    loc = compute_layout(graph, seed=CascadeConfig.seed)

    # cascade
    iterations = run_custom_cascade(graph, cascade_config)
    time_series = cascade_timeseries(iterations, graph.number_of_nodes())

    # multi-run cascade sizes
    sizes = cascade_size_monte_carlo(graph, cascade_config, runs=runs)

    # distributions
    degrees = np.array([degree for _, degree in graph.degree()], dtype=float)
    cluster_values = np.array(list(nx.clustering(graph.to_undirected()).values()), dtype=float)

    # traces
    edges = draw_edge(graph, loc, max_edges=6000)
    susceptible_nodes = draw_node(graph, loc, colors=[0] * graph.number_of_nodes())

    frames, _ = update_colors_per_frame(graph, iterations)

    # layout: 2x2
    diagrams = make_subplots(
        rows=2, 
        cols=2,
        specs=[[{"type": "scatter"}, {"type": "xy"}], [{"type": "xy"}, {"type": "xy"}]],
        subplot_titles=(
            f"{net_topology_label} - Animated Cascade",
            "Diffusion Rate",
            "Degree Distribution",
            "Cascade Size Distribution (Monte Carlo)"
        ),
        horizontal_spacing=0.08,
        vertical_spacing=0.14
    )

    # (1,1) network information cascade simulation animation
    diagrams.add_trace(edges, row=1, col=1)
    diagrams.add_trace(susceptible_nodes, row=1, col=1)

    # (1,2) diffusion rate curve
    diagrams.add_trace(go.Scatter(x=time_series["iter"], y=time_series["proportion_infected"], mode="lines", name="proportion of population infected"), row=1, col=2)
    diagrams.add_trace(go.Scatter(x=time_series["iter"], y=time_series["recently_infected"], mode="lines", name="recently infected"), row=1, col=2)

    # (2,1) degree distribution
    degree_counts = pd.Series(degrees).value_counts().sort_index()
    diagrams.add_trace(
        go.Scatter(
            x=degree_counts.index.astype(float),
            y=degree_counts.values.astype(float),
            mode="markers",
            name="degree counts"
        ),
        row=2,
        col=1
    )
    diagrams.update_xaxes(title_text="degree", row=2, col=1, type="log")
    diagrams.update_yaxes(title_text="count", row=2, col=1, type="log")

    # (2,2) cascade size distribution
    diagrams.add_trace(go.Histogram(x=sizes / graph.number_of_nodes(), nbinsx=20, name="final proportion infected"), row=2, col=2)

    # frames update: only node trace colors in (1,1)
    # In Plotly, frame data updates correspond to traces in order.
    # Here, edges is trace 0 and nodes is trace 1.
    # So we ensure frames update trace index 1 marker color.

    diagrams.frames = [
        go.Frame(
            name= frame.name,
            data=[go.Scatter(marker=frame.data[0].marker)], # only node colors
            traces=[1],
            layout=frame.layout
        )
        for frame in frames
    ]

    diagrams.update_layout(
        height=820,
        margin=dict(l=30, r=20, t=70, b=30),
        showlegend=False,
        hovermode="closest",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.05,
                y=1.08,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 60, "redraw": False},
                                "fromcurrent": True,
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                                "transition": {"duration": 0},
                            },
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                x=0.15,
                y=1.08,
                len=0.8,
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [frame.name],
                            {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}},
                        ],
                        label=frame.name,
                    )
                    for frame in diagrams.frames
                ],
            )
        ],
    )

     # clean axes for network
    diagrams.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)
    diagrams.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=1, col=1)

    diagrams.update_xaxes(title_text="iteration", row=1, col=2)
    diagrams.update_yaxes(title_text="value", row=1, col=2)

    diagrams.update_xaxes(title_text="final infected fraction", row=2, col=2)
    diagrams.update_yaxes(title_text="count", row=2, col=2)

    return diagrams, metrics