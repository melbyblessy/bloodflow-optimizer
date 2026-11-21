# BloodFlow Optimizer

BloodFlow Optimizer is an educational Flask web app for exploring blood inventory transfers between hospitals. It checks basic red-cell donor compatibility, estimates distances from hospital coordinates, allocates available units to demand, and estimates transportation costs.

> **For education only.** This project is not intended for clinical use or to guide real blood transfusions or transportation decisions.

## Requirements

- Python 3.10 or newer
- pip

## Run locally

Open a terminal in the project directory and create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell and install the dependency:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate and install with:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Start the development server:

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser. Stop the server with `Ctrl+C`.

## Use the app

1. On **Optimizer**, select how many hospitals to include (2–8).
2. Enter each hospital’s name and latitude/longitude in decimal degrees.
3. Set its available blood group and surplus units, then its required blood group and demand.
4. Set the estimated transportation cost per kilometre.
5. Select **Generate transfer plan** to view recommended transfers, estimated cost, and remaining inventory.
6. Select **Download CSV** to save the transfer rows. Use **Restore default data** to start again with the sample hospitals.

The **How it works** page in the sidebar describes each processing step in the app.

## How it works

The frontend and algorithm are kept separate:

- `app.py` contains the Flask routes, HTML/CSS interface, form validation, session storage, and CSV download.
- `algorithm.py` contains the blood-group compatibility table, distance and route functions, and transfer allocation logic.

The calculation follows these steps:

1. **Validate inputs.** The app checks hospital names are non-empty and unique, coordinates are in range (latitude −90 to 90, longitude −180 to 180), blood groups are supported, and unit counts and cost are non-negative.
2. **Check donor compatibility.** A lookup table in `algorithm.py` determines whether each donor blood group can serve the recipient’s requested group.
3. **Estimate distance.** The Haversine formula uses the two hospitals’ coordinates to estimate great-circle distance in kilometres.
4. **Estimate a route.** `astar()` applies A* search, using distance travelled as its path cost and estimated distance to the destination as its heuristic. In the current model every hospital is connected directly to every other hospital using straight-line distance.
5. **Allocate units.** `optimize_distribution()` visits recipients and donors in the order they appear in the submitted form. For each compatible pair, it transfers the smaller of the outstanding demand and donor’s remaining surplus. This is a greedy allocation strategy.
6. **Calculate transport cost and update inventory.** Each transfer cost is estimated as `distance × cost per kilometre × units`. Donor surplus and recipient demand are reduced, and the results page summarizes the transfers and remaining amounts.

## Limitations

- Distances are straight-line geographic estimates; there is no road network, route planning, traffic, or travel-time data. As a result, A* does not produce a real-world driving route in this version.
- Allocation is greedy and depends on hospital row order. It does not guarantee that the overall shortage or total transportation cost is globally minimized.
- The app does not model clinical eligibility, component types, expiry dates, storage, transportation constraints, or real-time inventory.
- Flask’s built-in development server is intended for local development, not production deployment.
