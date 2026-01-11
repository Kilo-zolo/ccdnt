# CascadeSim — Information Diffusion Lab

CascadeSim is an interactive simulation and visual analytics tool for exploring **information diffusion and attention cascades across network topologies**.

It is designed to investigate how **network structure, hubs, and local clustering** shape the spread, amplification, and decay of information over time.

The application is built with **Dash and Plotly**, powered by **NetworkX**, and supports animated cascades, structural metrics, and Monte Carlo analysis.

---

## Features

### Network Topologies
![Network topology diffusion](assets/network_topologies.gif)
- **Erdős–Rényi (ER)** — random graphs
- **Watts–Strogatz (WS)** — small-world networks
- **Barabási–Albert (BA)** — scale-free networks
- **Holme–Kim (HK)** — scale-free networks with triadic closure

### Cascade Model
- Broadcasting → reacting → decay dynamics
- Node-level **activity** and **influence**
- Degree-dependent amplification (hub effects)
- Stochastic, non-absorbing information flow

### Interactive Controls
- Network size (log scale)
- Initial broadcaster fraction (log scale)
- Influence probability (log scale)
- Iteration count
- Monte Carlo run count

### Visual Outputs
- Animated network cascade
- Temporal broadcaster–responder dynamics
- Degree distributions (log–log)
- Monte Carlo cascade size distributions

### Structural Metrics
- Average and maximum degree
- Degree inequality (Gini coefficient)
- Hub dominance (top 1% edge share)
- Average clustering coefficient
- Degree assortativity

---

## Conceptual Focus

CascadeSim is **not** a classical SIR or epidemic diffusion model.

Instead, it models:
- Attention propagation
- Bursty information spread
- Hub-driven amplification
- Local reinforcement via clustering

This makes it suitable for studying:
- Social media virality
- Meme and narrative diffusion
- Influence concentration
- Early-stage cascade predictability
- Structural risk in information networks

---

## Project Structure

```text
.
├── main.py                     # Dash app entry point
├── config.py                   # Topology and cascade configuration dataclasses
│
├── builders/
│   ├── dashboard_builders.py   # Assembles figures and metrics
│   ├── graph_builders.py       # Network topology construction
│   └── metric_builders.py      # Structural graph metrics
│
├── cascades/
│   ├── custom_cascades.py      # Core cascade dynamics
│   ├── monte_carlo_cascades.py # Repeated-run cascade sizing
│   └── timeseries_cascades.py  # Temporal aggregation utilities
│
├── layout/
│   ├── compute.py              # Graph layout computation
│   └── draw.py                 # Plotly rendering helpers
│
└── README.md
````

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cascadesim.git
cd cascadesim
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # macOS / Linux
# venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Python **3.9 or higher** is recommended.

---

## Running the App

```bash
python main.py
```

Then open your browser at:

```
http://localhost:8050
```

---

## Cascade Model

### Network

* Graph: `G = (V, E)`
* Number of nodes: `N = |V|`
* Node degree: `k_i` for node `i`

Each node `i` has:

* Activity level: `a_i ∈ [0, 1]`
* Influence probability: `β_i ∈ [0, 1]`

---

### Node States

At iteration `t`, each node has a state:

```
s_i(t) ∈ {0, 1, 2}

0 = idle
1 = broadcasting
2 = reacting
```

---

### Initial Seeding

A fraction `f₀` of nodes is selected uniformly at random as broadcasters:

```
|B(0)| = max(1, floor(f₀ · N))
```

All other nodes start in the idle state.

---

### Degree-Weighted Parameters

Node activity and influence scale linearly with degree:

```
a_i = a_min + (a_max − a_min) · (k_i / max_j k_j)
β_i = β_min + (β_max − β_min) · (k_i / max_j k_j)
```

This introduces **hub-amplified attention dynamics** without enforcing preferential attachment during diffusion.

---

### Cascade Dynamics (Per Iteration)

For each iteration `t = 1 … T`:

#### 1. Broadcaster Activation

Each broadcasting node `i ∈ B(t)` becomes active with probability:

```
P(active_i) = a_i
```

Inactive broadcasters do not emit influence.

---

#### 2. Influence Transmission

For an active broadcaster `i`, each neighbour `j ∈ N(i)` reacts with probability:

```
P(j reacts) = β_i
```

If successful:

```
s_j(t) = reacting
```

Active edges `(i, j)` are recorded for visualisation.

---

#### 3. Promotion to Broadcaster

Each reacting node is promoted to broadcaster with probability:

```
P(promote) = 0.15
```

---

#### 4. Decay Dynamics

Existing broadcasters persist with probability:

```
P(retain broadcaster) = 0.4
```

All other broadcasting and reacting nodes decay back to idle.

---

#### 5. Re-seeding

If no broadcasters remain:

```
|B(t+1)| = 0
```

A new seed set of size `floor(f₀ · N)` is introduced to prevent absorbing states.

---

### Observables

At each iteration:

* Number of broadcasters: `|B(t)|`
* Total responses: sum of all neighbour reactions
* Maximum single-node response (hub dominance proxy)
* Response variance across broadcasters

---

### Monte Carlo Cascade Size

For Monte Carlo run `r`:

```
S_r = sum over t of total_responses(t)
```

Normalised cascade size:

```
Ŝ_r = S_r / N
```

The distribution `{Ŝ_r}` captures cascade volatility and structural sensitivity.

---

## 🌐 Live Demo (Render)

A live deployment is available at:

👉 **[https://cascadesim.onrender.com/](https://cascadesim.onrender.com/)**

**Notes**

* Hosted on Render’s **free tier**
* Cold starts may take **30–60 seconds**
* Large networks may take longer on first load

If the app does not start after a reasonable wait, or something appears wrong, feel free to contact:

📧 **[krish5gupta25@gmail.com](mailto:krish5gupta25@gmail.com)**

---

## Future Work

* Threshold-based adoption models
* Memory and fatigue effects
* Directed networks
* External shocks and exogenous injections
* GNN-based cascade prediction
* Early-warning indicators for super-spreading events

---
