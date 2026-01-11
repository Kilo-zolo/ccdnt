# CascadeSim — Information Diffusion Lab

CascadeSim is an interactive simulation and visual analytics tool for exploring **information diffusion and attention cascades across network topologies**.  
It is designed to study how **network structure, hubs, and local clustering** shape the spread, amplification, and decay of information over time.

The app is built with **Dash + Plotly**, powered by **NetworkX**, and supports animated cascades, structural metrics, and Monte Carlo analysis.

---

## Features

- **Multiple network topologies**
  - Erdős–Rényi (random graphs)
  - Watts–Strogatz (small-world networks)
  - Barabási–Albert (scale-free networks)
  - Holme–Kim (scale-free with triadic closure)

- **Custom cascade model**
  - Broadcasting → reacting → decay dynamics
  - Node-level activity and influence
  - Degree-dependent amplification (hub effects)
  - Stochastic attention and triadic spread

- **Interactive controls**
  - Network size (log scale)
  - Initial broadcaster fraction (log scale)
  - Influence probability (log scale)
  - Iterations and Monte Carlo runs

- **Visual outputs**
  - Animated network cascade
  - Temporal response dynamics
  - Degree distributions (log–log)
  - Monte Carlo cascade size distributions

- **Structural metrics**
  - Degree inequality (Gini)
  - Hub dominance (top 1% edge share)
  - Clustering coefficient
  - Degree assortativity
  - Graph size and density indicators

---

## Conceptual Focus

CascadeSim is **not** a classical SIR epidemic model.

Instead, it models:
- **Attention propagation**
- **Information bursts**
- **Hub-driven amplification**
- **Local reinforcement via clustering**

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

## ⚙️ Installation

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

Python ≥ **3.9** is recommended.

---

## ▶️ Running the App

```bash
python main.py
```

Then open your browser at:

```
http://localhost:8050
```

---

## Mathematical Formulation of the Cascade Model

Let the network be a graph:

[
G = (V, E), \quad |V| = N
]

Each node ( i \in V ) has:

* Degree ( k_i )
* Activity level ( a_i \in [0,1] )
* Influence probability ( \beta_i \in [0,1] )

### Node States

At discrete time ( t ), each node has a state:
[
s_i(t) \in {0, 1, 2}
]

* ( 0 ): idle
* ( 1 ): broadcasting
* ( 2 ): reacting

---

### Initial Conditions

A fraction ( f_0 ) of nodes is selected uniformly at random as broadcasters:
[
|B(0)| = \max(1, \lfloor f_0 N \rfloor)
]

All other nodes begin in the idle state.

---

### Degree-Weighted Activity and Influence

Node parameters are assigned as:

[
a_i = a_{\min} + (a_{\max} - a_{\min}) \cdot \frac{k_i}{\max_j k_j}
]

[
\beta_i = \beta_{\min} + (\beta_{\max} - \beta_{\min}) \cdot \frac{k_i}{\max_j k_j}
]

This induces **hub-amplified attention dynamics** without enforcing preferential attachment during diffusion.

---

### Cascade Dynamics (Per Iteration)

For each time step ( t = 1, \dots, T ):

#### 1. Broadcaster Activation

Each broadcasting node ( i \in B(t) ) becomes active with probability:
[
\mathbb{P}(\text{active}_i) = a_i
]

---

#### 2. Influence Transmission

For an active broadcaster ( i ), each neighbour ( j \in \mathcal{N}(i) ) reacts with probability:
[
\mathbb{P}(j \text{ reacts}) = \beta_i
]

Successful reactions set:
[
s_j(t) \leftarrow 2
]

Active edges are recorded for visualisation.

---

#### 3. Promotion to Broadcaster

Each reacting node is promoted with probability:
[
\mathbb{P}(j \rightarrow \text{broadcast}) = p_{\text{promote}}
]

(Currently ( p_{\text{promote}} = 0.15 ))

---

#### 4. Decay Dynamics

Broadcasting nodes persist with probability:
[
\mathbb{P}(i \in B(t+1) \mid i \in B(t)) = p_{\text{retain}}
]

(Currently ( p_{\text{retain}} = 0.4 ))

All other active nodes decay back to idle.

---

#### 5. Re-seeding

If no broadcasters remain:
[
|B(t+1)| = 0
]

A new seed set of size ( \lfloor f_0 N \rfloor ) is introduced to maintain non-absorbing dynamics.

---

### Observables

At each iteration:

* Number of broadcasters:
  [
  B(t) = |{ i : s_i(t) = 1 }|
  ]

* Total responses:
  [
  R(t) = \sum_{i \in B(t)} \sum_{j \in \mathcal{N}(i)} \mathbb{I}_{\text{reaction}}
  ]

* Maximum single-node response

* Response variance across broadcasters

---

### Monte Carlo Cascade Size

For run ( r ):

[
S_r = \sum_{t=1}^{T} R_r(t)
]

Normalised cascade size:
[
\hat{S}_r = \frac{S_r}{N}
]

The distribution ( { \hat{S}_r } ) captures cascade volatility and structural sensitivity.

---

## 🌐 Live Demo (Render)

A live deployment is available at:

👉 **[https://cascadesim.onrender.com/](https://cascadesim.onrender.com/)**

**Note**

* Hosted on Render’s **free tier**
* Cold starts may take **30–60 seconds**
* Large networks may take longer on first load

If the app does not start after a reasonable wait, or something appears wrong, feel free to contact:

📧 **[krish5gupta25@gmail.com](mailto:krish5gupta25@gmail.com)**

---

## Intended Extensions

* Threshold-based adoption models
* Memory and fatigue effects
* Directed networks
* External shocks and exogenous injections
* GNN-based cascade prediction
* Early-warning indicators for super-spreading events

---

## 📜 License

MIT License — free to use, modify, and extend for research and educational purposes.

```

---