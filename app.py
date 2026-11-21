"""Flask frontend for BloodFlow Optimizer."""

import csv
import io

from flask import Flask, Response, redirect, render_template_string, request, session, url_for

from algorithm import BLOOD_TYPES, optimize_distribution


app = Flask(__name__)
app.secret_key = "bloodflow-optimizer-local-session"

DEFAULT_HOSPITALS = [
    ["City Hospital", 13.0827, 80.2707, "O-", 30, "A+", 20],
    ["North Clinic", 13.1000, 80.2500, "A+", 25, "B+", 35],
    ["Central Hospital", 13.0600, 80.2400, "B+", 40, "O+", 15],
    ["South Hospital", 12.9800, 80.2200, "AB+", 20, "AB-", 25],
    ["West Clinic", 13.0500, 80.1800, "O+", 30, "O-", 10],
    ["East Hospital", 13.0800, 80.3000, "B-", 25, "A-", 15],
    ["General Hospital", 13.1200, 80.2800, "A-", 20, "AB+", 10],
    ["Community Clinic", 13.0000, 80.2600, "AB-", 15, "B-", 10],
]

PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>BloodFlow Optimizer</title>
  <style>
    :root { color-scheme: light; --ink:#17243a; --muted:#6d7b8e; --line:#e2e8ef; --teal:#087f72; --pale:#f3f6f8; --soft:#eaf5f2; --red:#a93e36; }
    * { box-sizing:border-box; }
    body { margin:0; background:var(--pale); color:var(--ink); font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }
    .app-layout { display:grid; grid-template-columns:238px minmax(0,1fr); gap:28px; max-width:1540px; min-height:100vh; margin:0 auto; padding:24px; }
    .sidebar { position:sticky; top:24px; align-self:start; min-height:calc(100vh - 48px); padding:22px 16px; display:flex; flex-direction:column; border-radius:17px; color:#e8f2f4; background:linear-gradient(165deg,#142d40,#173e4a); box-shadow:0 10px 30px #17243a18; }
    .brand { display:flex; align-items:center; gap:11px; padding:4px 7px 23px; border-bottom:1px solid #ffffff20; }
    .brand-mark { display:grid; place-items:center; width:38px; height:38px; border-radius:12px; color:white; background:#128a79; font-weight:800; }
    .brand strong { display:block; font-size:15px; color:white; }
    .brand small { color:#aac0c9; font-size:11px; }
    .nav-label { margin:22px 9px 8px; color:#8faab5; font-size:10px; font-weight:750; letter-spacing:1.2px; text-transform:uppercase; }
    .nav-link { display:flex; align-items:center; gap:10px; margin:3px 0; padding:10px 11px; border-radius:9px; color:#c8d8dd; text-decoration:none; font-size:13px; font-weight:650; }
    .nav-link:hover,.nav-link.active { color:white; background:#ffffff18; }
    .nav-icon { width:20px; text-align:center; font-size:16px; }
    .sidebar-info { margin-top:auto; padding:13px; border:1px solid #ffffff20; border-radius:11px; background:#ffffff0b; }
    .sidebar-info b { display:block; margin-bottom:4px; color:#b9e4d9; font-size:12px; }
    .sidebar-info span { display:block; color:#c2d1d6; font-size:11px; line-height:1.55; }
    main { min-width:0; padding:14px 8px 40px 0; }
    .hero { padding:34px 38px; background:linear-gradient(115deg,#173449,#205b63); color:#fff; border-radius:18px; margin-bottom:24px; box-shadow:0 12px 32px #17344918; }
    .eyebrow { color:#a8ddd1; font-size:11px; font-weight:750; letter-spacing:1.6px; }
    h1 { margin:8px 0; font-size:34px; line-height:1.2; letter-spacing:-.7px; }
    .hero p { margin:0; color:#d2e0e8; }
    h2 { margin:0 0 6px; font-size:21px; letter-spacing:-.25px; }
    h3 { margin:0 0 12px; font-size:17px; }
    .muted, .hint { color:var(--muted); }
    .panel { background:white; border:1px solid var(--line); border-radius:15px; padding:24px; margin:18px 0; box-shadow:0 3px 14px #17243a08; }
    .settings { display:flex; align-items:end; gap:14px; flex-wrap:wrap; margin:20px 0 18px; padding:15px; background:#f7f9fa; border:1px solid #edf1f4; border-radius:11px; }
    label { display:block; font-size:13px; font-weight:650; }
    input, select { width:100%; min-width:100px; margin-top:5px; padding:9px 10px; border:1px solid #cfd8e2; border-radius:8px; color:var(--ink); background:white; font:inherit; }
    .settings label { width:190px; }
    .table-wrap { overflow-x:auto; border:1px solid var(--line); border-radius:10px; }
    table { width:100%; border-collapse:collapse; }
    th { text-align:left; font-size:11px; color:var(--muted); font-weight:750; padding:11px 8px; border-bottom:1px solid var(--line); background:#f8fafb; white-space:nowrap; }
    td { padding:8px 6px; border-bottom:1px solid #edf1f4; }
    td input, td select { min-width:95px; margin:0; padding:8px; }
    td:first-child input { min-width:150px; }
    button, .button { display:inline-block; background:var(--teal); color:white; border:0; border-radius:9px; padding:11px 17px; font:700 14px system-ui,sans-serif; text-decoration:none; cursor:pointer; transition:background .15s, transform .15s; }
    button:hover, .button:hover { background:#06675e; }
    button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible { outline:3px solid #54b9a7; outline-offset:2px; }
    .secondary { background:#e9f3f1; color:#075e55; }
    .secondary:hover { background:#d8ebe6; }
    .actions { display:flex; align-items:center; gap:10px; margin-top:16px; flex-wrap:wrap; }
    .alert { padding:13px 15px; background:#fff1ef; color:#85342d; border:1px solid #f1d2cd; border-radius:10px; margin:16px 0; }
    .metrics { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:18px 0 26px; }
    .metric { background:#f8fafb; border:1px solid var(--line); border-radius:12px; padding:17px; }
    .metric small { display:block; color:var(--muted); font-weight:700; font-size:11px; letter-spacing:.5px; }
    .metric strong { display:block; font-size:23px; margin:5px 0 1px; }
    .metric.shortage { background:#fff8f2; border-color:#f2dfcc; }
    .metric.shortage strong { color:#a45524; }
    .section-heading { display:flex; justify-content:space-between; align-items:flex-start; gap:14px; margin-bottom:16px; }
    .step { display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; margin-right:7px; border-radius:50%; color:#075e55; background:var(--soft); font-size:13px; vertical-align:2px; }
    .empty { padding:16px; background:#f7fafb; border-radius:9px; color:var(--muted); }
    .transfer-table td { padding:12px 9px; }
    .transfer-table td:first-child { font-weight:650; }
    .badge { display:inline-block; padding:3px 8px; color:#075e55; background:var(--soft); border-radius:20px; font-weight:700; font-size:12px; }
    .subhead { color:var(--muted); font-size:11px; font-weight:750; letter-spacing:.5px; text-transform:uppercase; }
    .section-note { margin-top:4px; font-size:13px; color:var(--muted); }
    .foot { text-align:center; color:var(--muted); font-size:12px; padding:24px 0 0; }
    .explainer-intro { max-width:760px; }
    .steps-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
    .explain-card { padding:19px; border:1px solid var(--line); border-radius:12px; background:#fff; }
    .explain-card p { margin:7px 0 0; color:var(--muted); font-size:14px; }
    .algo-tag { display:inline-block; margin-top:12px; padding:4px 8px; border-radius:6px; background:var(--soft); color:#075e55; font-size:11px; font-weight:750; }
    .formula { margin-top:12px; padding:11px 13px; border-left:3px solid var(--teal); border-radius:0 8px 8px 0; background:#f5faf8; font:13px ui-monospace,SFMono-Regular,Consolas,monospace; color:#31534e; }
    .note-card { padding:16px; border-radius:10px; border:1px solid #eee3c8; background:#fffaf0; color:#6c5730; font-size:13px; }
    @media(max-width:900px) { .app-layout{grid-template-columns:190px minmax(0,1fr);gap:18px;padding:16px}.sidebar{padding:18px 12px} }
    @media(max-width:760px) { .app-layout{display:block;padding:10px}.sidebar{position:static;min-height:0;padding:12px 14px;border-radius:13px}.brand{padding:2px 2px 11px}.sidebar .nav-label,.sidebar-info{display:none}.sidebar nav{display:flex;gap:8px;padding-top:9px}.nav-link{flex:1;justify-content:center;margin:0;padding:9px 7px}.sidebar .nav-icon{width:auto}.sidebar{margin-bottom:10px}main{padding:10px 4px 28px}.hero{padding:24px}.metrics{grid-template-columns:repeat(2,1fr)}.panel{padding:18px}.section-heading{display:block}.section-heading .button{margin-top:12px}.steps-grid{grid-template-columns:1fr} }
    @media(max-width:420px) { .metrics{grid-template-columns:1fr 1fr}.metric{padding:12px}.metric strong{font-size:19px} }
  </style>
</head>
<body><div class="app-layout">
  <aside class="sidebar">
    <div class="brand"><div class="brand-mark">BF</div><div><strong>BloodFlow</strong><small>Distribution planner</small></div></div>
    <div class="nav-label">Workspace</div>
    <nav aria-label="Main navigation">
      <a class="nav-link {% if active_page == 'optimizer' %}active{% endif %}" href="{{ url_for('index') }}"><span class="nav-icon">⌂</span>Optimizer</a>
      <a class="nav-link {% if active_page == 'guide' %}active{% endif %}" href="{{ url_for('how_it_works') }}"><span class="nav-icon">ⓘ</span>How it works</a>
    </nav>
    <div class="sidebar-info"><b>Planning overview</b><span>8 blood groups<br>Compatibility-aware allocation<br>Distance and cost estimates</span></div>
  </aside>
  <main>
  {% if info_page %}
  <header class="hero"><div class="eyebrow">THE PROCESS, STEP BY STEP</div><h1>How it works</h1><p>See how hospital data becomes a proposed blood transfer plan.</p></header>
  <section class="panel explainer-intro"><h2>From inventory to a plan</h2><p class="section-note">The optimizer reads the hospital rows, checks donor compatibility, estimates travel distance and cost, and updates the remaining inventory.</p></section>
  <section class="panel"><h2>Workflow and algorithms</h2><div class="section-note" style="margin-bottom:17px">Each step below maps to a specific part of the app.</div>
    <div class="steps-grid">
      <article class="explain-card"><h3><span class="step">1</span>Enter hospital data</h3><p>For each hospital, provide its name and coordinates, blood group and surplus available to donate, plus the required blood group and units needed. Set the transport rate and choose how many hospitals to include.</p><span class="algo-tag">Input and validation</span></article>
      <article class="explain-card"><h3><span class="step">2</span>Check blood compatibility</h3><p>The donor’s group is checked against a compatibility table. A transfer is considered only when that donor group can serve the recipient’s requested group.</p><span class="algo-tag">Compatibility lookup table</span></article>
      <article class="explain-card"><h3><span class="step">3</span>Estimate distance</h3><p>Hospital latitude and longitude are converted to radians and used to calculate great-circle distance over the Earth. The result is an approximate straight-line distance in kilometres.</p><span class="algo-tag">Haversine formula</span><div class="formula">distance = 2 × Earth radius × arcsin(…)</div></article>
      <article class="explain-card"><h3><span class="step">4</span>Find a route estimate</h3><p>The route function uses A* search. The path cost (g) is distance travelled so far; the heuristic (h) estimates the remaining distance to the destination. Hospital locations are treated as graph nodes.</p><span class="algo-tag">A* search</span></article>
      <article class="explain-card"><h3><span class="step">5</span>Allocate units and calculate cost</h3><p>For each recipient, the program scans donors in the displayed order and allocates compatible stock until the demand is met or eligible surplus runs out. It then calculates the transfer expense.</p><span class="algo-tag">Greedy allocation</span><div class="formula">transfer cost = distance × rate per km × units</div></article>
      <article class="explain-card"><h3><span class="step">6</span>Review results</h3><p>The plan shows proposed routes, units, distances, estimated expenses, and what remains at each hospital. Use the CSV download to save the transfer rows.</p><span class="algo-tag">Summary and inventory update</span></article>
    </div>
  </section>
  <section class="panel"><h2>What the model assumes</h2><div class="note-card">This is an educational planning demo. Its routing model connects every hospital directly using geographic distance, so it does not account for road networks, traffic, travel time, storage constraints, or clinical workflows. The greedy allocation depends on the order of hospitals and does not guarantee a globally lowest-cost plan. It is not intended for real clinical use.</div><div class="actions"><a class="button" href="{{ url_for('index') }}">Open optimizer</a></div></section>
  {% else %}
  <header class="hero">
    <div class="eyebrow">HEALTHCARE LOGISTICS</div>
    <h1>BloodFlow Optimizer</h1>
    <p>Plan compatible blood transfers between hospitals and estimate transport costs.</p>
  </header>
  {% if error %}<div class="alert" role="alert"><strong>Please check your entries.</strong><br>{{ error }}</div>{% endif %}
  <form method="post" action="{{ url_for('optimize') }}">
    <section class="panel">
      <div class="section-heading"><div><h2><span class="step">1</span>Hospital inventory</h2><div class="section-note">Enter each hospital’s location, available stock, and blood requirement.</div></div></div>
      <div class="settings">
        <label>Transport cost per km (₹)<input name="cost_per_km" type="number" min="0" step="0.5" value="{{ cost_per_km }}" required></label>
        <label>Number of hospitals<select name="count" onchange="resizeRows(this.value)">{% for n in range(2,9) %}<option value="{{ n }}" {% if n == hospitals|length %}selected{% endif %}>{{ n }} hospitals</option>{% endfor %}</select></label>
        <span class="hint">Use decimal latitude and longitude coordinates.</span>
      </div>
      <div class="table-wrap"><table><thead><tr><th>Hospital name</th><th>Latitude</th><th>Longitude</th><th><span class="subhead">Donates</span><br>Blood group</th><th>Surplus units</th><th><span class="subhead">Needs</span><br>Blood group</th><th>Required units</th></tr></thead>
      <tbody id="hospital-rows">{% for h in hospitals %}<tr>
        <td><input name="name[]" aria-label="Hospital name" value="{{ h[0] }}" required></td>
        <td><input name="lat[]" aria-label="Latitude" type="number" step="any" value="{{ h[1] }}" required></td>
        <td><input name="lon[]" aria-label="Longitude" type="number" step="any" value="{{ h[2] }}" required></td>
        <td><select name="blood[]" aria-label="Available blood group">{% for b in blood_types %}<option {% if b == h[3] %}selected{% endif %}>{{ b }}</option>{% endfor %}</select></td>
        <td><input name="surplus[]" aria-label="Surplus units" type="number" min="0" step="1" value="{{ h[4] }}" required></td>
        <td><select name="needed[]" aria-label="Required blood group">{% for b in blood_types %}<option {% if b == h[5] %}selected{% endif %}>{{ b }}</option>{% endfor %}</select></td>
        <td><input name="demand[]" aria-label="Required units" type="number" min="0" step="1" value="{{ h[6] }}" required></td>
      </tr>{% endfor %}</tbody></table></div>
      <div class="actions"><button type="submit">Generate transfer plan</button><button class="secondary" type="submit" formaction="{{ url_for('reset') }}" formmethod="post">Restore default data</button></div>
    </section>
  </form>
  {% if result %}
  <section class="panel">
    <div class="section-heading"><div><h2><span class="step">2</span>Transfer plan</h2><div class="section-note">Review the proposed transfers and remaining hospital needs.</div></div>{% if result.transfers %}<a class="button secondary" href="{{ url_for('download_report') }}">Download CSV</a>{% endif %}</div>
    <div class="metrics">
      <div class="metric"><small>UNITS TO TRANSFER</small><strong>{{ result.total_units }}</strong><span class="muted">blood units</span></div>
      <div class="metric"><small>UNIT-KILOMETRES</small><strong>{{ '%.2f'|format(result.total_distance) }}</strong><span class="muted">distance × units</span></div>
      <div class="metric"><small>ESTIMATED COST</small><strong>₹{{ '%.2f'|format(result.total_cost) }}</strong><span class="muted">transportation</span></div>
      <div class="metric shortage"><small>UNMET DEMAND</small><strong>{{ result.remaining_demand }}</strong><span class="muted">units still needed</span></div>
    </div>
    <h3>Recommended transfers</h3>
    {% if result.transfers %}<div class="table-wrap"><table class="transfer-table"><thead><tr><th>From</th><th>To</th><th>Blood group</th><th>Units</th><th>Distance</th><th>Estimated cost</th></tr></thead><tbody>
      {% for t in result.transfers %}<tr><td>{{ t['From'] }}</td><td>{{ t['To'] }}</td><td><span class="badge">{{ t['Blood Group'] }}</span></td><td>{{ t['Units'] }}</td><td>{{ t['Distance (km)'] }} km</td><td>₹{{ '%.2f'|format(t['Total Cost (₹)']) }}</td></tr>{% endfor %}
    </tbody></table></div>
    {% else %}<div class="empty">No compatible transfers are available for the entered inventory and requirements.</div>{% endif %}
  </section>
  <section class="panel"><h2>Remaining inventory</h2><div class="section-note" style="margin-bottom:14px">Stock and requirements after the proposed transfers.</div><div class="table-wrap"><table><thead><tr><th>Hospital</th><th>Available group</th><th>Remaining surplus</th><th>Required group</th><th>Unmet demand</th></tr></thead><tbody>
    {% for name,h in result.hospitals.items() %}<tr><td>{{ name }}</td><td><span class="badge">{{ h.blood }}</span></td><td>{{ h.surplus }}</td><td><span class="badge">{{ h.needed }}</span></td><td>{% if h.demand %}<strong style="color:var(--red)">{{ h.demand }}</strong>{% else %}0{% endif %}</td></tr>{% endfor %}
  </tbody></table></div></section>
  {% else %}<section class="panel"><span class="muted">Enter hospital details and optimize to generate a transfer plan.</span></section>{% endif %}
  {% endif %}
  <footer class="foot">BloodFlow Optimizer · Educational project · Not intended for clinical use</footer>
</main></div>
<script>
function resizeRows(count) {
  const rows = document.querySelectorAll('#hospital-rows tr');
  const selected = Number(count);
  rows.forEach((row, i) => row.hidden = i >= selected);
  // Only visible rows are submitted; hidden rows are disabled to avoid mismatched fields.
  rows.forEach((row, i) => row.querySelectorAll('input,select').forEach(el => el.disabled = i >= selected));
}
</script></body></html>"""


def render_page(hospitals=None, cost_per_km=15, result=None, error=None, info_page=False):
    return render_template_string(
        PAGE,
        hospitals=hospitals or [row[:] for row in DEFAULT_HOSPITALS[:4]],
        blood_types=BLOOD_TYPES,
        cost_per_km=cost_per_km,
        result=result,
        error=error,
        info_page=info_page,
        active_page="guide" if info_page else "optimizer",
    )


@app.get("/")
def index():
    result = session.get("result")
    return render_page(
        hospitals=session.get("input_hospitals"),
        cost_per_km=session.get("cost_per_km", 15),
        result=result,
    )


@app.get("/how-it-works")
def how_it_works():
    return render_page(info_page=True)


@app.post("/optimize")
def optimize():
    fields = [request.form.getlist(key) for key in ("name[]", "lat[]", "lon[]", "blood[]", "surplus[]", "needed[]", "demand[]")]
    names, lats, lons, bloods, surpluses, needed, demands = fields
    submitted_rows = []
    for values in zip(*fields):
        name, lat, lon, blood, surplus, need, demand = values
        try:
            submitted_rows.append([name, float(lat), float(lon), blood, int(surplus), need, int(demand)])
        except (ValueError, TypeError):
            submitted_rows.append([name, lat, lon, blood, surplus, need, demand])
    entered_cost = request.form.get("cost_per_km", "15")
    try:
        count = int(request.form.get("count", "0"))
        cost_per_km = float(entered_cost)
        if not 2 <= count <= 8 or any(len(values) != count for values in fields):
            raise ValueError
        inputs = []
        hospitals = {}
        for i in range(count):
            name = names[i].strip()
            lat, lon = float(lats[i]), float(lons[i])
            surplus, demand = int(surpluses[i]), int(demands[i])
            if (not name or name in hospitals or not -90 <= lat <= 90 or
                    not -180 <= lon <= 180 or surplus < 0 or demand < 0 or
                    bloods[i] not in BLOOD_TYPES or needed[i] not in BLOOD_TYPES):
                raise ValueError
            inputs.append([name, lat, lon, bloods[i], surplus, needed[i], demand])
            hospitals[name] = {"lat": lat, "lon": lon, "blood": bloods[i], "surplus": surplus, "needed": needed[i], "demand": demand}
        if cost_per_km < 0:
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        return render_page(
            hospitals=submitted_rows or None,
            cost_per_km=entered_cost,
            error="Use unique hospital names, valid coordinates (latitude −90 to 90, longitude −180 to 180), and non-negative whole-number units.",
        ), 400

    transfers, hospitals = optimize_distribution(hospitals, cost_per_km)
    result = {
        "transfers": transfers,
        "hospitals": hospitals,
        "total_units": sum(t["Units"] for t in transfers),
        "total_cost": sum(t["Total Cost (₹)"] for t in transfers),
        "total_distance": sum(t["Distance (km)"] * t["Units"] for t in transfers),
        "remaining_demand": sum(h["demand"] for h in hospitals.values()),
    }
    session["input_hospitals"] = inputs
    session["cost_per_km"] = cost_per_km
    session["result"] = result
    return redirect(url_for("index"))


@app.post("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


@app.get("/report.csv")
def download_report():
    transfers = session.get("result", {}).get("transfers", [])
    output = io.StringIO()
    columns = ["From", "To", "Blood Group", "Units", "Distance (km)", "Cost per Unit (₹)", "Total Cost (₹)"]
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    writer.writerows(transfers)
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=blood_distribution_report.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
