"""Blood transfer planner using A* search, CSP backtracking and hill climbing."""

import heapq
import math

BLOOD_TYPES = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

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
    """Haversine distance in kilometres."""
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def km(h, a, b):
    return distance(h[a]["lat"], h[a]["lon"], h[b]["lat"], h[b]["lon"])


# 1. A* Search: shortest route, heuristic = straight-line distance to goal.
def astar(start, goal, h):
    queue, seen = [(0, 0, start)], set()
    while queue:
        _, cost, node = heapq.heappop(queue)
        if node == goal:
            return cost
        if node in seen:
            continue
        seen.add(node)
        for nxt in h:
            if nxt not in seen:
                g = cost + km(h, node, nxt)
                heapq.heappush(queue, (g + km(h, nxt, goal), g, nxt))
    return 0


# 2. CSP Backtracking: give each recipient one compatible donor that can
#    cover its full demand, without exceeding any donor's surplus.
def backtrack(recipients, domains, h, assignment, used):
    if len(assignment) == len(recipients):
        return assignment
    r = recipients[len(assignment)]
    for d in domains[r] + [None]:
        if d is None or used.get(d, 0) + h[r]["demand"] <= h[d]["surplus"]:
            assignment[r] = d
            if d:
                used[d] = used.get(d, 0) + h[r]["demand"]
            if backtrack(recipients, domains, h, assignment, used):
                return assignment
            if d:
                used[d] -= h[r]["demand"]
            del assignment[r]
    return None


def allocate(order, h, cost_per_km):
    """Fill demand in the given order. Returns (score, transfers, surplus, demand)."""
    surplus = {n: x["surplus"] for n, x in h.items()}
    demand = {n: x["demand"] for n, x in h.items()}
    transfers, cost = [], 0
    for d, r, dist in order:
        units = min(surplus[d], demand[r])
        if units > 0:
            surplus[d] -= units
            demand[r] -= units
            transfers.append((d, r, dist, units))
            cost += dist * cost_per_km * units
    return sum(demand.values()) * 1_000_000 + cost, transfers, surplus, demand


# 3. Hill Climbing: swap pairs in the allocation order while it improves.
def hill_climb(order, h, cost_per_km):
    best = allocate(order, h, cost_per_km)[0]
    improved = True
    while improved:
        improved = False
        for i in range(len(order)):
            for j in range(i + 1, len(order)):
                order[i], order[j] = order[j], order[i]
                score = allocate(order, h, cost_per_km)[0]
                if score < best:
                    best, improved = score, True
                else:
                    order[i], order[j] = order[j], order[i]
    return order


def optimize_distribution(hospitals, cost_per_km):
    h = hospitals
    pairs = [(d, r, astar(d, r, h))
             for r in h if h[r]["demand"] > 0
             for d in h if d != r and h[d]["surplus"] > 0
             and h[r]["needed"] in COMPATIBILITY[h[d]["blood"]]]

    recipients = sorted({r for _, r, _ in pairs})
    domains = {r: [d for d, rr, _ in sorted(pairs, key=lambda p: p[2])
                   if rr == r and h[d]["surplus"] >= h[r]["demand"]] for r in recipients}
    assignment = backtrack(recipients, domains, h, {}, {}) or {}

    primary = [p for p in pairs if assignment.get(p[1]) == p[0]]
    rest = sorted((p for p in pairs if p not in primary), key=lambda p: p[2])
    order = hill_climb(primary + rest, h, cost_per_km)
    _, allocated, surplus, demand = allocate(order, h, cost_per_km)

    transfers = [{
        "From": d,
        "To": r,
        "Blood Group": h[d]["blood"],
        "Units": units,
        "Distance (km)": round(dist, 2),
        "Cost per Unit (₹)": round(dist * cost_per_km, 2),
        "Total Cost (₹)": round(dist * cost_per_km * units, 2),
    } for d, r, dist, units in allocated]

    for n in h:
        h[n]["surplus"], h[n]["demand"] = surplus[n], demand[n]
    return transfers, h
