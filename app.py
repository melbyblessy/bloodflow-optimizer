
import streamlit as st
import pandas as pd
import math
import heapq

st.set_page_config(
    page_title="BloodFlow Optimizer",
    page_icon="🩸",
    layout="wide"
)

# ---------------- DESIGN AND STYLING ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #F4F7FB;
    color: #17243A;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #17243A;
    font-weight: 700 !important;
    letter-spacing: -0.8px;
}

.hero {
    background: linear-gradient(120deg, #101E35, #17445B, #116B70);
    padding: 42px;
    border-radius: 22px;
    color: white;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(20,40,70,0.12);
}

.hero h1 {
    color: white !important;
    font-size: 42px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: -2px;
    margin: 12px 0;
}

.hero p {
    color: #C5D8E6;
    font-size: 14px;
}

.eyebrow {
    color: #65DEC5;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
}

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 23px;
    font-weight: 700;
    color: #17243A;
    margin-top: 25px;
    margin-bottom: 5px;
}

.section-subtitle {
    color: #8290A3;
    font-size: 13px;
    margin-bottom: 18px;
}

.metric-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #E6ECF3;
    box-shadow: 0 4px 15px rgba(20,40,70,0.04);
    min-height: 125px;
}

.metric-label {
    color: #8290A3;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

.metric-value {
    color: #17243A;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
    margin-top: 10px;
}

.metric-note {
    color: #0F9F89;
    font-size: 11px;
    margin-top: 5px;
}

.transfer-card {
    background: white;
    border: 1px solid #E5EBF3;
    border-left: 4px solid #0FAD91;
    padding: 20px;
    border-radius: 13px;
    margin-bottom: 12px;
}

.transfer-route {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #17243A;
}

.transfer-info {
    color: #8290A2;
    font-size: 12px;
    margin-top: 9px;
}

.stButton > button {
    background: #0F9F89;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 11px 20px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    min-height: 45px;
}

.stButton > button:hover {
    background: #087D6D;
    color: white;
    border: none;
}

.stDownloadButton > button {
    background: #172D49;
    color: white;
    border-radius: 10px;
    border: none;
}

[data-testid="stSidebar"] {
    background: #111F35;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

[data-testid="stSidebar"] p {
    color: #B2C2D5;
}

[data-testid="stDataFrame"],
[data-testid="stDataEditor"] {
    border: 1px solid #E6ECF3;
    border-radius: 12px;
    overflow: hidden;
}

.stTextInput input,
.stNumberInput input {
    border-radius: 9px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <div class="eyebrow">TYPE - A* | HEALTHCARE LOGISTICS</div>
    <h1>BloodFlow Optimizer</h1>
    <p>Intelligent blood inventory distribution and transportation planning.</p>
    <div style="margin-top:20px;color:#A9C8DB;font-size:12px;">
        8 BLOOD GROUPS &nbsp; | &nbsp;
        A* PATHFINDING &nbsp; | &nbsp;
        TRANSPORT COST OPTIMIZATION
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------- BLOOD COMPATIBILITY ----------------

blood_types = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

compatibility = {
    "O-": blood_types,
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}


# ---------------- DISTANCE CALCULATION ----------------

def distance(lat1, lon1, lat2, lon2):
    radius = 6371

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    a = math.sin((lat2 - lat1) / 2) ** 2
    b = math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a + b), math.sqrt(1 - a - b))

    return radius * c


# ---------------- A STAR ALGORITHM ----------------

def astar(start, goal, hospitals):

    queue = [(0, 0, start)]
    visited = set()

    while queue:

        _, cost, current = heapq.heappop(queue)

        if current == goal:
            return cost

        if current in visited:
            continue

        visited.add(current)

        for neighbour in hospitals:

            if neighbour == current or neighbour in visited:
                continue

            step = distance(
                hospitals[current]["lat"],
                hospitals[current]["lon"],
                hospitals[neighbour]["lat"],
                hospitals[neighbour]["lon"]
            )

            new_cost = cost + step

            heuristic = distance(
                hospitals[neighbour]["lat"],
                hospitals[neighbour]["lon"],
                hospitals[goal]["lat"],
                hospitals[goal]["lon"]
            )

            heapq.heappush(
                queue,
                (new_cost + heuristic, new_cost, neighbour)
            )

    return 0


# ---------------- SIDEBAR ----------------

st.sidebar.markdown("## 🩸 BloodFlow")
st.sidebar.caption("DISTRIBUTION CONTROL PANEL")

st.sidebar.markdown("---")
st.sidebar.markdown("### Transportation Settings")

cost_per_km = st.sidebar.number_input(
    "Cost per kilometre (₹)",
    min_value=0.0,
    value=15.0,
    step=1.0
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Hospital Settings")

number = st.sidebar.slider(
    "Number of hospitals",
    min_value=2,
    max_value=8,
    value=4
)

st.sidebar.info(
    "Enter the latitude and longitude of each hospital."
)

st.sidebar.markdown("---")
st.sidebar.caption("TEAM TYPE - A* | COLLEGE AI PROJECT")


# ---------------- DEFAULT HOSPITAL DATA ----------------

default_data = [
    ["City Hospital", 13.0827, 80.2707, "O-", 30, "A+", 20],
    ["North Clinic", 13.1000, 80.2500, "A+", 25, "B+", 35],
    ["Central Hospital", 13.0600, 80.2400, "B+", 40, "O+", 15],
    ["South Hospital", 12.9800, 80.2200, "AB+", 20, "AB-", 25],
    ["West Clinic", 13.0500, 80.1800, "O+", 30, "O-", 10],
    ["East Hospital", 13.0800, 80.3000, "B-", 25, "A-", 15],
    ["General Hospital", 13.1200, 80.2800, "A-", 20, "AB+", 10],
    ["Community Clinic", 13.0000, 80.2600, "AB-", 15, "B-", 10]
]

df = pd.DataFrame(
    default_data[:number],
    columns=[
        "Hospital", "Latitude", "Longitude",
        "Available Blood", "Surplus Units",
        "Required Blood", "Required Units"
    ]
)


# ---------------- HOSPITAL INVENTORY ----------------

st.markdown(
    '<div class="section-title">Hospital Inventory</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-subtitle">Manage blood availability and requirements for each hospital.</div>',
    unsafe_allow_html=True
)

edited_df = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    key="hospital_editor",
    column_config={
        "Hospital": st.column_config.TextColumn("Hospital Name"),
        "Latitude": st.column_config.NumberColumn("Latitude", format="%.5f"),
        "Longitude": st.column_config.NumberColumn("Longitude", format="%.5f"),
        "Available Blood": st.column_config.SelectboxColumn(
            "Available Group", options=blood_types
        ),
        "Surplus Units": st.column_config.NumberColumn(
            "Surplus Units", min_value=0, step=1
        ),
        "Required Blood": st.column_config.SelectboxColumn(
            "Required Group", options=blood_types
        ),
        "Required Units": st.column_config.NumberColumn(
            "Required Units", min_value=0, step=1
        )
    }
)


# ---------------- OPTIMIZATION BUTTON ----------------

st.markdown("")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Distribution Optimization")
    st.caption("Calculate compatible transfers, distances and transportation costs.")

with col2:
    run = st.button("⚡ Optimize Distribution", use_container_width=True)


if run:

    hospitals = {}
    valid = True

    for _, row in edited_df.iterrows():

        name = str(row["Hospital"]).strip()

        if not name or name in hospitals:
            valid = False
            break

        try:
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            surplus = int(row["Surplus Units"])
            demand = int(row["Required Units"])
        except (ValueError, TypeError):
            valid = False
            break

        if not -90 <= lat <= 90 or not -180 <= lon <= 180:
            valid = False
            break

        if surplus < 0 or demand < 0:
            valid = False
            break

        if row["Available Blood"] not in blood_types:
            valid = False
            break

        if row["Required Blood"] not in blood_types:
            valid = False
            break

        hospitals[name] = {
            "lat": lat,
            "lon": lon,
            "blood": row["Available Blood"],
            "surplus": surplus,
            "needed": row["Required Blood"],
            "demand": demand
        }

    if not valid or len(hospitals) < 2:

        st.error("Please check hospital names, coordinates and unit values.")

        if "transfers" in st.session_state:
            del st.session_state["transfers"]
            del st.session_state["hospitals"]

    else:

        transfers = []

        for receiver in hospitals:

            demand = hospitals[receiver]["demand"]
            required_blood = hospitals[receiver]["needed"]

            for donor in hospitals:

                if donor == receiver or demand <= 0:
                    continue

                available_blood = hospitals[donor]["blood"]

                if required_blood in compatibility[available_blood]:

                    available_units = hospitals[donor]["surplus"]

                    if available_units > 0:

                        units = min(demand, available_units)

                        km = astar(donor, receiver, hospitals)

                        cost_per_unit = km * cost_per_km
                        total_cost = cost_per_unit * units

                        transfers.append({
                            "From": donor,
                            "To": receiver,
                            "Blood Group": available_blood,
                            "Units": units,
                            "Distance (km)": round(km, 2),
                            "Cost per Unit (₹)": round(cost_per_unit, 2),
                            "Total Cost (₹)": round(total_cost, 2)
                        })

                        hospitals[donor]["surplus"] -= units
                        hospitals[receiver]["demand"] -= units
                        demand -= units

        st.session_state["transfers"] = transfers
        st.session_state["hospitals"] = hospitals


# ---------------- RESULTS ----------------

if "transfers" in st.session_state:

    transfers = st.session_state["transfers"]
    hospitals = st.session_state["hospitals"]

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Distribution Overview</div>',
        unsafe_allow_html=True
    )

    total_units = sum(t["Units"] for t in transfers)

    total_cost = sum(t["Total Cost (₹)"] for t in transfers)

    total_distance = sum(
        t["Distance (km)"] * t["Units"] for t in transfers
    )

    remaining_demand = sum(
        h["demand"] for h in hospitals.values()
    )

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("UNITS TRANSFERRED", total_units, "Blood units distributed"),
        ("TOTAL DISTANCE", f"{total_distance:.2f}", "Unit-kilometres"),
        ("TRANSPORT COST", f"₹{total_cost:,.2f}", "Estimated expense"),
        ("REMAINING SHORTAGE", remaining_demand, "Units still required")
    ]

    for col, (label, value, note) in zip(
        [c1, c2, c3, c4], metrics
    ):

        with col:

            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    # TRANSFER DETAILS

    st.markdown(
        '<div class="section-title">Recommended Transfers</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-subtitle">Suggested blood movements between hospitals.</div>',
        unsafe_allow_html=True
    )

    if transfers:

        for t in transfers:

            st.markdown(f"""
            <div class="transfer-card">
                <div class="transfer-route">
                    {t['From']} &nbsp; → &nbsp; {t['To']}
                </div>
                <div class="transfer-info">
                    BLOOD GROUP: {t['Blood Group']} &nbsp; | &nbsp;
                    UNITS: {t['Units']} &nbsp; | &nbsp;
                    DISTANCE: {t['Distance (km)']} km
                </div>
                <div style="margin-top:12px;font-weight:800;color:#0F9F89;">
                    Total transportation cost: ₹{t['Total Cost (₹)']:,.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        result_df = pd.DataFrame(transfers)

        st.download_button(
            "⬇ Download Transfer Report",
            result_df.to_csv(index=False).encode("utf-8"),
            "blood_distribution_report.csv",
            "text/csv"
        )

    else:

        st.warning("No compatible blood transfers were found.")

    # REMAINING INVENTORY

    st.markdown("---")

    st.markdown(
        '<div class="section-title">Remaining Inventory</div>',
        unsafe_allow_html=True
    )

    inventory = []

    for name, h in hospitals.items():

        inventory.append({
            "Hospital": name,
            "Available Blood Group": h["blood"],
            "Remaining Surplus": h["surplus"],
            "Required Blood Group": h["needed"],
            "Remaining Demand": h["demand"]
        })

    st.dataframe(
        pd.DataFrame(inventory),
        use_container_width=True,
        hide_index=True
    )

    # ALGORITHM EXPLANATION

    st.markdown("---")

    with st.expander("How does the system work?"):

        st.markdown("""
        **1. Blood Compatibility**

        Checks whether the donor blood group is compatible with the recipient.

        **2. A* Algorithm**

        Uses the distance already travelled (g) and estimated remaining
        distance (h) to find the shortest route.

        **3. Distance Calculation**

        Uses hospital coordinates and the Haversine formula.

        **4. Transportation Cost**

        Total cost = Distance × Cost per kilometre × Units transferred.

        **5. Inventory Management**

        Updates the surplus and shortage after each transfer.
        """)

else:

    st.markdown("---")

    st.info(
        "Enter hospital details and click Optimize Distribution "
        "to generate your transfer plan."
    )


# ---------------- FOOTER ----------------

st.markdown("---")

st.markdown("""
<div style="text-align:center;padding:22px;color:#8B98A9;font-size:12px;">
    <b style="color:#52647A;">BLOODFLOW OPTIMIZER</b><br>
    Built by Team Type - A* | Educational AI Project<br>
    Not intended for real clinical use.
</div>
""", unsafe_allow_html=True)
