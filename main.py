from __future__ import annotations
import os
import math
from dash import Dash, dcc, html, Input, Output, State

from config import DEFAULT_NET_TOPOLOGIES, NetTopologyConfig, CascadeConfig
from builders import dashboard_builders

app = Dash(__name__)
app.title = "CascadeSim — Information Diffusion Lab"

app.layout = html.Div(
    style={
        "background": "radial-gradient(circle at top, #0f172a, #020617)",
        "minHeight": "100vh",
        "color": "#e5e7eb",
        "fontFamily": "Inter, system-ui, sans-serif",
        "padding": "16px",
    },
    children=[
        html.H2("CascadeSim", style={"marginBottom": "4px"}),
        html.Div("Information Diffusion Lab", style={"opacity": 0.7}),
        html.Hr(),

        html.Div(
            style={"display": "flex", "gap": "16px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    style={
                        "width": "320px",
                        "background": "#020617",
                        "padding": "16px",
                        "borderRadius": "16px",
                        "boxShadow": "0 10px 40px rgba(0,0,0,0.5)",
                    },
                    children=[
                        html.H4("Network Topology"),

                        dcc.Dropdown(
                            id="topology",
                            options=[{"label": k, "value": k} for k in DEFAULT_NET_TOPOLOGIES],
                            value="Barbasi-Albert",
                            clearable=False,
                            style={
                                "backgroundColor": "#e5e7eb",
                                "color": "#020617",
                            },
                        ),

                        html.Hr(),

                        html.Label("Network Size (log)", style={"opacity": 0.85}),
                        dcc.Slider(
                            id="n_log",
                            min=1,
                            max=3,
                            step=0.01,
                            value=2,
                            marks={1: "10", 2: "100", 3: "1000"},
                        ),

                        html.Label("Initial Broadcaster Fraction (log)", style={"opacity": 0.85}),
                        dcc.Slider(
                            id="seed_log",
                            min=-3,
                            max=-1,
                            step=0.05,
                            value=-2,
                            marks={-3: "0.001", -2: "0.01", -1: "0.1"},
                        ),

                        html.Label("Influence Probability (log)", style={"opacity": 0.85}),
                        dcc.Slider(
                            id="influence_log",
                            min=-3,
                            max=-0.5,
                            step=0.05,
                            value=-1,
                            marks={-3: "0.001", -2: "0.01", -1: "0.1"},
                        ),

                        html.Label("Iterations", style={"opacity": 0.85}),
                        dcc.Slider(id="iters", min=20, max=200, step=10, value=60),

                        html.Label("Monte Carlo Runs", style={"opacity": 0.85}),
                        dcc.Slider(id="mc_runs", min=5, max=60, step=5, value=20),

                        html.Br(),
                        html.Button(
                            "Run Simulation",
                            id="recompute",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "background": "#2563eb",
                                "border": "none",
                                "padding": "10px",
                                "borderRadius": "10px",
                                "color": "white",
                                "fontWeight": 600,
                                "cursor": "pointer",
                            },
                        ),
                    ],
                ),

                html.Div(
                    style={"flex": 1},
                    children=[
                        dcc.Tabs(
                            value="tab-cascade",
                            colors={
                                "border": "#020617",
                                "primary": "#2563eb",
                                "background": "#020617",
                            },
                            children=[
                                dcc.Tab(
                                    label="Animated Cascade",
                                    value="tab-cascade",
                                    style={
                                        "backgroundColor": "#020617",
                                        "color": "#9ca3af",
                                        "padding": "10px",
                                        "fontWeight": 500,
                                    },
                                    selected_style={
                                        "backgroundColor": "#020617",
                                        "color": "#e5e7eb",
                                        "padding": "10px",
                                        "fontWeight": 600,
                                        "borderBottom": "2px solid #2563eb",
                                    },
                                    children=[
                                        dcc.Graph(
                                            id="cascade-fig",
                                            config={"displayModeBar": False},
                                            style={"height": "82vh"},
                                        )
                                    ],
                                ),
                                dcc.Tab(
                                    label="Analysis & Metrics",
                                    value="tab-analysis",
                                    style={
                                        "backgroundColor": "#020617",
                                        "color": "#9ca3af",
                                        "padding": "10px",
                                        "fontWeight": 500,
                                    },
                                    selected_style={
                                        "backgroundColor": "#020617",
                                        "color": "#e5e7eb",
                                        "padding": "10px",
                                        "fontWeight": 600,
                                        "borderBottom": "2px solid #2563eb",
                                    },
                                    children=[
                                        html.Div(
                                            style={
                                                "display": "grid",
                                                "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                                                "gap": "12px",
                                                "marginTop": "12px",
                                            },
                                            children=[
                                                dcc.Graph(id="dynamics-fig", config={"displayModeBar": False}),
                                                dcc.Graph(id="degree-fig", config={"displayModeBar": False}),
                                                dcc.Graph(id="mc-fig", config={"displayModeBar": False}),
                                            ],
                                        ),
                                        html.Div(
                                            style={
                                                "marginTop": "16px",
                                                "background": "#020617",
                                                "padding": "16px",
                                                "borderRadius": "16px",
                                            },
                                            children=[
                                                html.H4("Topology Summary"),
                                                html.Div(id="metrics-table"),
                                            ],
                                        ),
                                    ],
                                ),
                            ],
                        )
                    ],
                ),
            ],
        ),
    ],
)

@app.callback(
    Output("cascade-fig", "figure"),
    Output("dynamics-fig", "figure"),
    Output("degree-fig", "figure"),
    Output("mc-fig", "figure"),
    Output("metrics-table", "children"),
    Input("recompute", "n_clicks"),
    State("topology", "value"),
    State("n_log", "value"),
    State("seed_log", "value"),
    State("influence_log", "value"),
    State("iters", "value"),
    State("mc_runs", "value"),
)
def update_fig(_, topology_label, n_log, seed_log, influence_log, iters, mc_runs):

    n = int(round(10 ** n_log))
    seed_frac = 10 ** seed_log
    influence = 10 ** influence_log

    base = DEFAULT_NET_TOPOLOGIES[topology_label]
    topo_cfg = NetTopologyConfig(**{**base.__dict__, "nodes": n})

    cas_cfg = CascadeConfig(
        fraction_infected=seed_frac,
        influence_probability=influence,
        iterations=int(iters),
        seed=42,
    )

    cascade_fig, dynamics_fig, degree_fig, mc_fig, metrics = dashboard_builders.build_dashboard(
        topology_label, topo_cfg, cas_cfg, runs=int(mc_runs)
    )

    rows = []
    for k, v in metrics.items():
        sval = "n/a" if isinstance(v, float) and not math.isfinite(v) else f"{v:.4g}"
        rows.append(html.Tr([html.Td(k), html.Td(sval)]))

    table = html.Table(
        [html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")]))]
        + [html.Tbody(rows)],
        style={"width": "100%", "borderCollapse": "collapse"},
    )

    return cascade_fig, dynamics_fig, degree_fig, mc_fig, table


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))