from typing import Tuple, Dict
import numpy as np
import networkx as nx
import pandas as pd
import plotly.graph_objects as go

from config import NetTopologyConfig, CascadeConfig
from builders.graph_builders import build_graph
from builders.metric_builders import graph_metrics
from layout.compute import compute_layout
from layout.draw import (
    draw_node,
    draw_edge,
    draw_active_edges,
    update_colors_per_frame,
)
from cascades.custom_cascades import run_custom_cascade
from cascades.monte_carlo_cascades import cascade_size_monte_carlo
from cascades.timeseries_cascades import cascade_timeseries


def build_dashboard(
    net_topology_label: str,
    net_topology_config: NetTopologyConfig,
    cascade_config: CascadeConfig,
    runs: int,
) -> Tuple[go.Figure, go.Figure, go.Figure, go.Figure, Dict[str, float]]:

    graph = build_graph(net_topology_config)

    degrees = dict(graph.degree())
    max_degree = max(degrees.values()) if degrees else 1

    for node in graph.nodes():
        graph.nodes[node]["activity"] = 0.2 + 0.8 * (degrees[node] / max_degree)
        graph.nodes[node]["influence"] = 0.02 + 0.08 * (degrees[node] / max_degree)

    metrics = graph_metrics(graph)

    loc = compute_layout(graph, seed=cascade_config.seed)

    iterations = run_custom_cascade(graph, cascade_config)
    time_series = cascade_timeseries(iterations, graph.number_of_nodes())
    sizes = cascade_size_monte_carlo(graph, cascade_config, runs=runs)

    static_edges = draw_edge(graph, loc, max_edges=6000)

    active_edges_trace = go.Scatter(
        x=[],
        y=[],
        mode="lines",
        line=dict(color="#2563eb", width=2.2),
        hoverinfo="none",
        name="active_edges",
    )

    nodes = draw_node(
        graph,
        loc,
        colors=[0] * graph.number_of_nodes(),
    )

    cascade_fig = go.Figure(data=[static_edges, active_edges_trace, nodes])

    frames, _ = update_colors_per_frame(graph, iterations)

    cascade_fig.frames = [
        go.Frame(
            name=frame.name,
            data=[
                draw_active_edges(
                    iterations[int(frame.name)]["active_edges"],
                    loc,
                ),
                go.Scatter(marker=frame.data[0].marker),
            ],
            traces=[1, 2],
            layout=frame.layout,
        )
        for frame in frames
    ]

    cascade_fig.update_layout(
        height=800,
        title=dict(
            text=f"{net_topology_label} — Information Cascade",
            x=0.5,
            y=0.94,
            xanchor="center",
        ),
        margin=dict(l=20, r=20, t=90, b=30),
        showlegend=False,
        hovermode="closest",
        paper_bgcolor="white",
        plot_bgcolor="white",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.05,
                y=1.12,
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 280},
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[[None], {"mode": "immediate"}],
                    ),
                ],
            )
        ],
    )

    cascade_fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
    cascade_fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

    dynamics_fig = go.Figure()
    dynamics_fig.add_trace(
        go.Scatter(
            x=time_series["iteration_number"],
            y=time_series["mean_responses"],
            mode="lines",
            name="Mean responses",
        )
    )
    dynamics_fig.add_trace(
        go.Scatter(
            x=time_series["iteration_number"],
            y=time_series["max_responses"],
            mode="lines",
            name="Max responses (hub)",
        )
    )
    dynamics_fig.update_layout(
        title="Broadcaster → Responder Dynamics",
        height=360,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    dynamics_fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    dynamics_fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

    deg_vals = np.array([d for _, d in graph.degree()], dtype=float)
    degree_counts = pd.Series(deg_vals).value_counts().sort_index()

    degree_fig = go.Figure()
    degree_fig.add_trace(
        go.Scatter(
            x=degree_counts.index,
            y=degree_counts.values,
            mode="markers",
        )
    )
    degree_fig.update_layout(
        title="Degree Distribution",
        xaxis_type="log",
        yaxis_type="log",
        height=360,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    degree_fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    degree_fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

    mc_fig = go.Figure()
    mc_fig.add_trace(
        go.Histogram(
            x=sizes / graph.number_of_nodes(),
            nbinsx=20,
        )
    )
    mc_fig.update_layout(
        title="Cascade Size Distribution (Monte Carlo)",
        height=360,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
    )
    mc_fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
    mc_fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")

    return cascade_fig, dynamics_fig, degree_fig, mc_fig, metrics