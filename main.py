from __future__ import annotations

import math
from config import DEFAULT_NET_TOPOLOGIES, NetTopologyConfig, CascadeConfig
from builders import dashboard_builders
from dash import Dash, dcc, html, Input, Output, State

app = Dash(__name__)
app.title = "Cascade Topology Demo"

app.layout = html.Div(
    style={"fontFamily": "Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif", "padding": "16px"},
    children=[
        html.H2("Comparative Cascade Dynamics Across Network Topologies", style={"marginBottom": "6px"}),
        html.Div(
            "Animated cascades + structure metrics + distributions — ER / WS / BA / Holme–Kim",
            style={"opacity": 0.8, "marginBottom": "16px"},
        ),

        html.Div(
            style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "alignItems": "end"},
            children=[
                html.Div(
                    children=[
                        html.Label("Topology"),
                        dcc.Dropdown(
                            id="topology",
                            options=[{"label": k, "value": k} for k in DEFAULT_NET_TOPOLOGIES.keys()],
                            value="Barbasi-Albert",
                            clearable=False,
                            style={"width": "280px"},
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Label("Nodes (n)"),
                        dcc.Slider(id="n", min=400, max=2500, step=100, value=1200, marks=None, tooltip={"placement": "bottom"}),
                    ],
                    style={"width": "280px"},
                ),
                html.Div(
                    children=[
                        html.Label("Initial infected fraction"),
                        dcc.Slider(id="seed_frac", min=0.001, max=0.05, step=0.001, value=0.01, marks=None, tooltip={"placement": "bottom"}),
                    ],
                    style={"width": "280px"},
                ),
                html.Div(
                    children=[
                        html.Label("Influence prob per edge"),
                        dcc.Slider(id="influence", min=0.005, max=0.25, step=0.005, value=0.05, marks=None, tooltip={"placement": "bottom"}),
                    ],
                    style={"width": "280px"},
                ),
                html.Div(
                    children=[
                        html.Label("Iterations"),
                        dcc.Slider(id="iters", min=20, max=200, step=10, value=60, marks=None, tooltip={"placement": "bottom"}),
                    ],
                    style={"width": "280px"},
                ),
                html.Div(
                    children=[
                        html.Label("Cascade MC runs"),
                        dcc.Slider(id="mc_runs", min=5, max=60, step=5, value=25, marks=None, tooltip={"placement": "bottom"}),
                    ],
                    style={"width": "280px"},
                ),
                html.Button("Recompute", id="recompute", n_clicks=0, style={"height": "38px", "padding": "0 14px"}),
            ],
        ),

        html.Div(style={"height": "14px"}),

        html.Div(
            style={"display": "grid", "gridTemplateColumns": "1fr 320px", "gap": "12px", "alignItems": "start"},
            children=[
                dcc.Graph(id="dash-fig", config={"displayModeBar": False}),
                html.Div(
                    style={
                        "border": "1px solid rgba(0,0,0,0.1)",
                        "borderRadius": "12px",
                        "padding": "12px",
                        "boxShadow": "0 1px 10px rgba(0,0,0,0.04)",
                    },
                    children=[
                        html.H4("Topology Summary", style={"marginTop": 0}),
                        html.Div(id="metrics-table"),
                        html.Hr(),
                        html.Div(
                            [
                                html.H4("Notes", style={"marginTop": 0}),
                                html.Ul(
                                    [
                                        html.Li("BA/HK: hubs ⇒ faster global cascades (when hubs get infected)."),
                                        html.Li("WS/HK: clustering ⇒ local bursts + community jumps."),
                                        html.Li("ER: more uniform spread; needs enough connectivity/probability."),
                                    ]
                                ),
                            ],
                            style={"opacity": 0.85},
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("dash-fig", "figure"),
    Output("metrics-table", "children"),
    Input("recompute", "n_clicks"),
    State("topology", "value"),
    State("n", "value"),
    State("seed_frac", "value"),
    State("influence", "value"),
    State("iters", "value"),
    State("mc_runs", "value"),
)
def update_fig(_, topology_label, n, seed_frac, influence, iters, mc_runs):
    base = DEFAULT_NET_TOPOLOGIES[topology_label]

    # copy + patch n
    topo_cfg = NetTopologyConfig(**{**base.__dict__, "nodes": int(n)})

    # small safety clamps
    if topo_cfg.name in ("BA", "HK"):
        topo_cfg.no_linked_edges = max(1, min(topo_cfg.no_linked_edges, topo_cfg.nodes - 1))
    if topo_cfg.name == "WS":
        topo_cfg.no_linked_nodes = max(2, min(topo_cfg.no_linked_nodes, topo_cfg.nodes - 1))
        if topo_cfg.no_linked_nodes % 2 == 1:
            topo_cfg.no_linked_nodes += 1

    cas_cfg = CascadeConfig(
        fraction_infected=float(seed_frac),
        influence_probability=float(influence),
        iterations=int(iters),
        seed=42,
    )

    fig, metrics = dashboard_builders.build_dashboard(topology_label, topo_cfg, cas_cfg, runs=int(mc_runs))

    # pretty metrics
    rows = []
    for k, v in metrics.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            sval = "n/a"
        else:
            sval = f"{v:.4g}" if isinstance(v, float) else str(v)
        rows.append(html.Tr([html.Td(k), html.Td(sval)]))

    table = html.Table(
        [html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")]))] + [html.Tbody(rows)],
        style={"width": "100%", "borderCollapse": "collapse"},
    )

    return fig, table


if __name__ == "__main__":
    app.run(debug=True, port=8050)
