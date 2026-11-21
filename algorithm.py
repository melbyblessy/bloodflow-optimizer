"""Blood compatibility and transfer planning algorithms."""

import heapq
import math


BLOOD_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

# Red-cell donor compatibility: keys are donor groups and values are
# recipient groups that can receive those cells.
COMPATIBILITY = {
    "O-": BLOOD_TYPES,
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"],
}


def distance(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in kilometres."""
    radius = 6371
    lat1, lat2 = math.radians(lat1), math.radians(lat2)
    lon1, lon2 = math.radians(lon1), math.radians(lon2)
    a = math.sin((lat2 - lat1) / 2) ** 2
    b = math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a + b), math.sqrt(1 - a - b))


def astar(start, goal, hospitals):
    """Find a shortest route in the complete graph of hospital locations."""
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
                hospitals[current]["lat"], hospitals[current]["lon"],
                hospitals[neighbour]["lat"], hospitals[neighbour]["lon"],
            )
            new_cost = cost + step
            heuristic = distance(
                hospitals[neighbour]["lat"], hospitals[neighbour]["lon"],
                hospitals[goal]["lat"], hospitals[goal]["lon"],
            )
            heapq.heappush(queue, (new_cost + heuristic, new_cost, neighbour))
    return 0


def optimize_distribution(hospitals, cost_per_km):
    """Allocate compatible donor inventory to hospital demand in input order.

    Each hospital is a mapping with lat, lon, blood, surplus, needed, and
    demand fields. Returns transfer rows and the updated hospital mappings.
    """
    transfers = []
    for receiver, recipient in hospitals.items():
        for donor, source in hospitals.items():
            if donor == receiver or recipient["demand"] <= 0:
                continue
            if recipient["needed"] not in COMPATIBILITY[source["blood"]]:
                continue
            if source["surplus"] <= 0:
                continue

            units = min(recipient["demand"], source["surplus"])
            km = astar(donor, receiver, hospitals)
            unit_cost = km * cost_per_km
            transfers.append({
                "From": donor,
                "To": receiver,
                "Blood Group": source["blood"],
                "Units": units,
                "Distance (km)": round(km, 2),
                "Cost per Unit (₹)": round(unit_cost, 2),
                "Total Cost (₹)": round(unit_cost * units, 2),
            })
            source["surplus"] -= units
            recipient["demand"] -= units
    return transfers, hospitals
