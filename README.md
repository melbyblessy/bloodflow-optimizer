# BloodFlow Optimizer

BloodFlow Optimizer is an educational web application for exploring blood inventory distribution between hospitals. It uses blood-group compatibility checking, geographical distance calculations, graph-based route finding, and optimization algorithms to generate blood transfer plans while estimating transportation costs.

🌐 **Live Demo:** https://bloodflow-five.vercel.app/

> **For education only.** This project is not intended for clinical use or to guide real blood transfusions or transportation decisions.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

Open a terminal in the project directory and create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell and install the dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate and install with:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the application:

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal in a browser. Stop the server with `Ctrl+C`.

## Use the app

1. Open the **Optimizer** page to configure the hospital network.
2. Enter the hospital details, including geographical coordinates, available blood groups, surplus units, and required blood groups.
3. Configure the transportation cost parameters.
4. Generate a transfer plan to calculate compatible blood transfers between hospitals.
5. Explore the optimized allocation, transportation routes, estimated distances, and costs.
6. Review remaining inventory and unmet blood requirements.
7. Download the generated transfer plan as a CSV file for further analysis.

The **How It Works** section provides an overview of the algorithms and processing stages used by the application.

## How it works

The application combines blood compatibility checking, graph algorithms, and optimization techniques to generate hospital-to-hospital transfer plans.

The calculation follows these steps:

1. **Validate inputs.** Hospital information, geographical coordinates, blood groups, inventory quantities, and transportation parameters are checked before processing.
2. **Check donor compatibility.** A blood-group compatibility lookup determines whether available blood can be allocated to a hospital's requirements.
3. **Calculate geographical distances.** The Haversine formula estimates the distance between hospital coordinates in kilometres.
4. **Construct the hospital network.** K-Nearest Neighbours identifies nearby hospital connections, while Prim's Minimum Spanning Tree helps establish network connectivity.
5. **Find transportation routes.** Uniform Cost Search (UCS) and A* Search are used to determine routes through the hospital network based on accumulated distance and heuristic estimates.
6. **Optimize blood allocation.** An initial greedy allocation is improved using Simulated Annealing to explore alternative transfer combinations and reduce unmet demand and transportation effort.
7. **Calculate transportation costs.** Transfer distances, allocated units, and transportation rates are used to estimate the total distribution cost.
8. **Generate results.** The application presents transfer recommendations, remaining inventory, unmet requirements, and downloadable CSV reports.

## Algorithms used

| Algorithm | Purpose |
|---|---|
| Haversine Formula | Calculates geographical distances |
| K-Nearest Neighbours | Identifies nearby hospital connections |
| Prim's Minimum Spanning Tree | Establishes network connectivity |
| Uniform Cost Search | Finds minimum-cost paths |
| A* Search | Performs heuristic-based route finding |
| Greedy Allocation | Generates an initial transfer plan |
| Simulated Annealing | Improves the initial allocation |

The Simulated Annealing optimization uses an objective function that considers both unmet blood demand and transportation effort:

`Energy = 10,000 × Unmet Units + Unit-Kilometres`

This gives priority to satisfying hospital demand while also considering transportation efficiency.

## Limitations

- The application uses geographical distance estimates and does not necessarily represent actual road distances, traffic conditions, or travel times.
- Route optimization depends on the constructed hospital network and does not account for real-world road restrictions.
- Simulated Annealing is a heuristic optimization technique and does not guarantee a globally optimal solution.
- Results depend on the accuracy of the hospital inventory, coordinates, and transportation cost inputs.
- The application does not model clinical eligibility, blood component separation, expiry dates, storage conditions, or real-time inventory.
- Transportation cost estimates are theoretical and may differ from actual logistics expenses.
- This application is an educational prototype and has not been clinically validated.

---

**BloodFlow Optimizer – Exploring AI-driven optimization for healthcare logistics.**
