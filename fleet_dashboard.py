"""
Fleet Dashboard Generator
Reads fleet_status.csv and produces a self-contained fleet_dashboard.html.
Uses Python Standard Library only (Leaflet.js loaded from CDN by the browser).
"""

import csv
import html
import os
import json
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

STATUS_COLOURS = {
    "active":      "#22c55e",
    "idle":        "#f97316",
    "offline":     "#ef4444",
    "low_battery": "#eab308",
}

STATUS_BG = {
    "active":      "#dcfce7",
    "idle":        "#ffedd5",
    "offline":     "#fee2e2",
    "low_battery": "#fef9c3",
}

STATUS_TEXT = {
    "active":      "#15803d",
    "idle":        "#c2410c",
    "offline":     "#b91c1c",
    "low_battery": "#854d0e",
}

VALID_STATUSES = set(STATUS_COLOURS.keys())

# ---------------------------------------------------------------------------
# 1. Load & Validate CSV
# ---------------------------------------------------------------------------

def load_csv(path: str) -> list:
    devices = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            device = {}

            device_id = (row.get("device_id") or "").strip()
            if not device_id:
                continue
            device["device_id"] = html.escape(device_id)

            name = (row.get("name") or "").strip()
            device["name"] = html.escape(name) if name else device["device_id"]

            status = (row.get("status") or "offline").strip().lower()
            device["status"] = status if status in VALID_STATUSES else "offline"
            device["status_raw"] = html.escape(status)

            try:
                batt = float(row.get("battery_pct", ""))
                device["battery_pct"] = max(0, min(100, round(batt)))
                device["battery_valid"] = True
            except (ValueError, TypeError):
                device["battery_pct"] = None
                device["battery_valid"] = False

            try:
                device["lat"] = float(row.get("lat", ""))
                device["lon"] = float(row.get("lon", ""))
                device["coords_valid"] = True
            except (ValueError, TypeError):
                device["lat"] = None
                device["lon"] = None
                device["coords_valid"] = False

            last_seen_str = (row.get("last_seen") or "").strip()
            try:
                dt = datetime.strptime(last_seen_str, "%Y-%m-%d %H:%M:%S")
                if dt > datetime.now():
                    device["last_seen"] = None
                    device["last_seen_str"] = "Invalid date"
                else:
                    device["last_seen"] = dt
                    device["last_seen_str"] = html.escape(last_seen_str)
            except ValueError:
                device["last_seen"] = None
                device["last_seen_str"] = "Unknown"

            device["location"] = html.escape((row.get("location") or "Unknown").strip())
            devices.append(device)

    return devices

# ---------------------------------------------------------------------------
# 2. Summary Statistics
# ---------------------------------------------------------------------------

def calculate_summary(devices: list) -> dict:
    summary = {"total": len(devices), "active": 0, "idle": 0, "offline": 0, "low_battery": 0, "other": 0}
    for d in devices:
        s = d["status"]
        if s in summary:
            summary[s] += 1
        else:
            summary["other"] += 1
    return summary

# ---------------------------------------------------------------------------
# 3. Human-readable "time since last seen"
# ---------------------------------------------------------------------------

def calculate_last_seen(dt) -> str:
    if dt is None:
        return "Unknown"
    now = datetime.now()
    delta = now - dt
    total_seconds = int(delta.total_seconds())
    if total_seconds < 0:
        return "Future date"
    if total_seconds < 60:
        return f"{total_seconds} second{'s' if total_seconds != 1 else ''} ago"
    if total_seconds < 3600:
        m = total_seconds // 60
        return f"{m} minute{'s' if m != 1 else ''} ago"
    if total_seconds < 86400:
        h = total_seconds // 3600
        return f"{h} hour{'s' if h != 1 else ''} ago"
    d = total_seconds // 86400
    return f"{d} day{'s' if d != 1 else ''} ago"

# ---------------------------------------------------------------------------
# 4. Leaflet Map — emits JS marker data (accurate lat/lon)
# ---------------------------------------------------------------------------

def generate_map_js(devices: list) -> str:
    """Build the JavaScript array of marker objects for Leaflet."""
    markers = []
    for d in devices:
        if not d["coords_valid"]:
            continue
        colour = STATUS_COLOURS.get(d["status"], "#94a3b8")
        batt_str = f"{d['battery_pct']}%" if d["battery_valid"] else "N/A"
        since = calculate_last_seen(d["last_seen"])
        status_label = d["status_raw"].replace("_", " ").title()
        bg = STATUS_BG.get(d["status"], "#f1f5f9")
        txt = STATUS_TEXT.get(d["status"], "#475569")

        popup_html = (
            f"<div style='font-family:system-ui,sans-serif;min-width:200px'>"
            f"<div style='font-weight:700;font-size:14px;margin-bottom:6px;color:#1e293b'>{d['device_id']} — {d['name']}</div>"
            f"<span style='background:{bg};color:{txt};padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600'>{status_label}</span>"
            f"<table style='margin-top:10px;width:100%;font-size:12px;border-collapse:collapse'>"
            f"<tr><td style='color:#64748b;padding:2px 0'>Battery</td><td style='font-weight:600;text-align:right'>{batt_str}</td></tr>"
            f"<tr><td style='color:#64748b;padding:2px 0'>Location</td><td style='font-weight:600;text-align:right'>{d['location']}</td></tr>"
            f"<tr><td style='color:#64748b;padding:2px 0'>Last seen</td><td style='font-weight:600;text-align:right'>{since}</td></tr>"
            f"<tr><td style='color:#64748b;padding:2px 0'>Coords</td><td style='font-weight:600;text-align:right;font-size:10px'>{d['lat']:.4f}, {d['lon']:.4f}</td></tr>"
            f"</table></div>"
        )

        marker = {
            "lat": d["lat"],
            "lon": d["lon"],
            "colour": colour,
            "status": d["status"],
            "popup": popup_html,
            "id": d["device_id"],
        }
        markers.append(json.dumps(marker))

    return "[\n" + ",\n".join(markers) + "\n]"

# ---------------------------------------------------------------------------
# 5. Device Table
# ---------------------------------------------------------------------------

def battery_bar(pct, valid: bool) -> str:
    if not valid or pct is None:
        return '<span class="batt-na">N/A</span>'
    if pct >= 50:
        bar_colour = "#22c55e"
    elif pct >= 20:
        bar_colour = "#f97316"
    else:
        bar_colour = "#ef4444"
    fill_w = round(pct * 28 / 100)
    return (
        f'<span class="batt-wrap" title="{pct}%">'
        f'<svg width="36" height="14" viewBox="0 0 36 14" xmlns="http://www.w3.org/2000/svg">'
        f'<rect x="0" y="1" width="32" height="12" rx="2" fill="none" stroke="#475569" stroke-width="1.5"/>'
        f'<rect x="32" y="4" width="3" height="6" rx="1" fill="#475569"/>'
        f'<rect x="1.5" y="2.5" width="{fill_w}" height="9" rx="1.5" fill="{bar_colour}"/>'
        f'</svg>'
        f'<span class="batt-pct">{pct}%</span>'
        f'</span>'
    )

def status_badge(status: str, raw: str) -> str:
    bg = STATUS_BG.get(status, "#f1f5f9")
    txt = STATUS_TEXT.get(status, "#475569")
    label = raw.replace("_", " ").title()
    return f'<span class="badge" style="background:{bg};color:{txt}">{label}</span>'

def generate_table(devices: list) -> str:
    rows = []
    for i, d in enumerate(devices):
        since = calculate_last_seen(d["last_seen"])
        row_class = "row-even" if i % 2 == 0 else "row-odd"
        batt_html = battery_bar(d["battery_pct"], d["battery_valid"])
        badge_html = status_badge(d["status"], d["status_raw"])
        rows.append(f"""
        <tr class="{row_class}">
          <td class="mono">{d['device_id']}</td>
          <td>{d['name']}</td>
          <td>{badge_html}</td>
          <td>{batt_html}</td>
          <td>{d['location']}</td>
          <td class="mono small">{d['last_seen_str']}</td>
          <td class="small muted">{since}</td>
        </tr>""")

    return f"""
<div class="table-wrap">
  <table id="fleet-table" class="fleet-table">
    <thead>
      <tr>
        <th onclick="sortTable(0)">Device ID ⇅</th>
        <th onclick="sortTable(1)">Vehicle ⇅</th>
        <th onclick="sortTable(2)">Status ⇅</th>
        <th onclick="sortTable(3)">Battery ⇅</th>
        <th onclick="sortTable(4)">Location ⇅</th>
        <th onclick="sortTable(5)">Last Seen ⇅</th>
        <th>Since</th>
      </tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</div>
"""

# ---------------------------------------------------------------------------
# 6. KPI Cards
# ---------------------------------------------------------------------------

def generate_summary_cards(summary: dict) -> str:
    cards = [
        ("Total Devices", summary["total"],       "#6366f1", "🚛"),
        ("Active",        summary["active"],       "#22c55e", "✅"),
        ("Idle",          summary["idle"],         "#f97316", "⏸"),
        ("Offline",       summary["offline"],      "#ef4444", "🔴"),
        ("Low Battery",   summary["low_battery"],  "#eab308", "🔋"),
    ]
    parts = []
    for label, count, colour, icon in cards:
        parts.append(f"""
    <div class="kpi-card" style="--accent:{colour}">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-count" style="color:{colour}">{count}</div>
      <div class="kpi-label">{label}</div>
    </div>""")
    return '<div class="kpi-grid">' + "".join(parts) + "</div>"

# ---------------------------------------------------------------------------
# 7. Full HTML with Leaflet map
# ---------------------------------------------------------------------------

def generate_dashboard(devices: list, summary: dict) -> str:
    now_str = datetime.now().strftime("%d %b %Y, %H:%M:%S")
    cards_html = generate_summary_cards(summary)
    table_html = generate_table(devices)
    markers_js = generate_map_js(devices)
    legend_items = "".join(
        f'<span class="leg-dot" style="background:{c}"></span>{s.replace("_"," ").title()} '
        for s, c in STATUS_COLOURS.items()
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Fleet Command — Live Dashboard</title>

<!-- Leaflet CSS (loaded by browser at open time) -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
:root {{
  --bg:        #020818;
  --surface:   #0d1526;
  --surface2:  #141f35;
  --border:    #1e2d47;
  --text:      #e2e8f0;
  --muted:     #64748b;
  --accent:    #3b82f6;
  --radius:    12px;
  --font-mono: "JetBrains Mono","Fira Code",ui-monospace,monospace;
  --font-body: "Inter","Segoe UI",system-ui,sans-serif;
}}
body {{
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.6;
  min-height: 100vh;
}}
.shell {{ max-width: 1280px; margin: 0 auto; padding: 0 24px 48px; }}

/* Header */
.site-header {{
  display:flex; align-items:center; justify-content:space-between;
  padding: 20px 0 18px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 32px;
  flex-wrap: wrap; gap: 12px;
}}
.header-brand {{ display:flex; align-items:center; gap:12px; }}
.brand-mark {{
  width:38px; height:38px;
  background: linear-gradient(135deg,#3b82f6,#8b5cf6);
  border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  font-size:20px;
}}
.brand-name {{ font-size:18px; font-weight:700; letter-spacing:-0.3px; color:#f1f5f9; }}
.brand-sub  {{ font-size:12px; color:var(--muted); }}
.header-meta {{ font-size:12px; color:var(--muted); text-align:right; }}
.live-dot {{
  display:inline-block; width:8px; height:8px;
  border-radius:50%; background:#22c55e; margin-right:6px;
  animation: blink 2s infinite;
}}
@keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.3; }} }}

/* Section label */
.section-label {{
  font-size:11px; font-weight:600; letter-spacing:0.08em;
  text-transform:uppercase; color:var(--muted); margin-bottom:14px;
}}

/* KPI */
.kpi-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:14px; margin-bottom:36px;
}}
.kpi-card {{
  background:var(--surface); border:1px solid var(--border);
  border-top:3px solid var(--accent); border-radius:var(--radius);
  padding:18px 16px 14px;
  display:flex; flex-direction:column; align-items:flex-start; gap:4px;
  transition:transform 0.15s,box-shadow 0.15s;
}}
.kpi-card:hover {{ transform:translateY(-2px); box-shadow:0 8px 24px rgba(0,0,0,0.4); }}
.kpi-icon  {{ font-size:20px; margin-bottom:6px; }}
.kpi-count {{ font-size:32px; font-weight:800; line-height:1; font-variant-numeric:tabular-nums; }}
.kpi-label {{ font-size:12px; color:var(--muted); }}

/* Map section */
.map-section {{ margin-bottom:36px; }}
.map-header {{
  display:flex; align-items:center; justify-content:space-between;
  flex-wrap:wrap; gap:8px; margin-bottom:12px;
}}
.map-legend {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; font-size:12px; color:var(--muted); }}
.leg-dot {{ display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:4px; vertical-align:middle; }}

/* Leaflet container */
#fleet-map {{
  height: 500px;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  overflow: hidden;
}}
/* Override Leaflet popup to match dark theme */
.leaflet-popup-content-wrapper {{
  border-radius: 10px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
  padding: 0 !important;
}}
.leaflet-popup-content {{
  margin: 14px 16px !important;
  font-size: 13px;
}}
.leaflet-popup-tip-container {{ display:none; }}
.leaflet-control-zoom a {{
  background: #1e2d47 !important;
  color: #e2e8f0 !important;
  border-color: #2d4163 !important;
}}
.leaflet-control-zoom a:hover {{ background:#2d4163 !important; }}

/* Table */
.table-section {{ margin-bottom:36px; }}
.table-controls {{
  display:flex; align-items:center; justify-content:space-between;
  flex-wrap:wrap; gap:10px; margin-bottom:12px;
}}
.search-box {{
  background:var(--surface2); border:1px solid var(--border); border-radius:8px;
  color:var(--text); padding:7px 14px; font-size:13px; width:240px;
  outline:none; transition:border-color 0.2s;
}}
.search-box:focus {{ border-color:var(--accent); }}
.table-wrap {{ overflow-x:auto; border-radius:var(--radius); border:1px solid var(--border); }}
.fleet-table {{ width:100%; border-collapse:collapse; font-size:13px; }}
.fleet-table thead tr {{ background:var(--surface2); border-bottom:1px solid var(--border); }}
.fleet-table th {{
  padding:11px 14px; text-align:left;
  font-size:11px; font-weight:600; letter-spacing:0.05em; text-transform:uppercase;
  color:var(--muted); cursor:pointer; user-select:none; white-space:nowrap;
}}
.fleet-table th:hover {{ color:var(--text); }}
.fleet-table td {{ padding:10px 14px; border-bottom:1px solid #111c30; vertical-align:middle; }}
.row-even {{ background:var(--surface); }}
.row-odd  {{ background:#0a1220; }}
.fleet-table tr:last-child td {{ border-bottom:none; }}
.fleet-table tbody tr:hover {{ background:#162035; }}
.badge {{
  display:inline-block; padding:2px 9px; border-radius:20px;
  font-size:11px; font-weight:600; letter-spacing:0.03em; white-space:nowrap;
}}
.batt-wrap {{ display:flex; align-items:center; gap:6px; white-space:nowrap; }}
.batt-pct  {{ font-size:12px; color:var(--muted); font-variant-numeric:tabular-nums; }}
.batt-na   {{ color:var(--muted); font-size:12px; }}
.mono  {{ font-family:var(--font-mono); font-size:12px; }}
.small {{ font-size:12px; }}
.muted {{ color:var(--muted); }}

/* Footer */
.site-footer {{
  border-top:1px solid var(--border); padding-top:18px;
  font-size:12px; color:var(--muted);
  display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
}}

@media (max-width:640px) {{
  .kpi-count {{ font-size:26px; }}
  .search-box {{ width:100%; }}
  #fleet-map {{ height:360px; }}
}}
</style>
</head>
<body>
<div class="shell">

  <header class="site-header">
    <div class="header-brand">
      <div class="brand-mark">🚛</div>
      <div>
        <div class="brand-name">Fleet Command</div>
        <div class="brand-sub">GPS Tracking Dashboard</div>
      </div>
    </div>
    <div class="header-meta">
      <span class="live-dot"></span>Generated {now_str}<br>
      {summary['total']} devices tracked
    </div>
  </header>

  <p class="section-label">Fleet Overview</p>
  {cards_html}

  <section class="map-section">
    <div class="map-header">
      <p class="section-label" style="margin-bottom:0">Live Map</p>
      <div class="map-legend">{legend_items}</div>
    </div>
    <div id="fleet-map"></div>
  </section>

  <section class="table-section">
    <div class="table-controls">
      <p class="section-label" style="margin-bottom:0">Device List</p>
      <input class="search-box" type="text" id="search-input"
             placeholder="Search by ID, name, location…"
             oninput="filterTable(this.value)"/>
    </div>
    {table_html}
  </section>

  <footer class="site-footer">
    <span>Fleet Command · {now_str}</span>
    <span>{summary['active']} active · {summary['offline']} offline · {summary['low_battery']} low battery</span>
  </footer>

</div>

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
// ---- Leaflet Map ----
(function() {{
  var map = L.map('fleet-map', {{
    center: [-27.0, 134.0],
    zoom: 5,
    zoomControl: true
  }});

  // Dark-themed tile layer (CartoDB Dark Matter — no API key needed)
  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 19
  }}).addTo(map);

  // Status colour map
  var colours = {{
    active:      '#22c55e',
    idle:        '#f97316',
    offline:     '#ef4444',
    low_battery: '#eab308'
  }};

  // Device data
  var markers = {markers_js};

  markers.forEach(function(m) {{
    var colour = m.colour;
    var isActive = m.status === 'active';

    // Custom circle marker with optional pulse for active
    var circleOuter = L.circleMarker([m.lat, m.lon], {{
      radius: isActive ? 14 : 0,
      color: colour,
      fillColor: colour,
      fillOpacity: 0.15,
      weight: 0
    }});

    var circle = L.circleMarker([m.lat, m.lon], {{
      radius: 8,
      color: '#ffffff',
      fillColor: colour,
      fillOpacity: 1,
      weight: 2
    }});

    if (isActive) circleOuter.addTo(map);

    circle.addTo(map).bindPopup(m.popup, {{
      maxWidth: 260,
      minWidth: 220
    }});

    // Show device ID label on hover
    circle.bindTooltip(m.id, {{
      permanent: false,
      direction: 'top',
      offset: [0, -10],
      className: 'dev-label'
    }});
  }});
}})();

// ---- Table Sort ----
var sortDir = {{}};
function sortTable(col) {{
  var tbody = document.querySelector('#fleet-table tbody');
  var rows = Array.from(tbody.rows);
  sortDir[col] = sortDir[col] === 'asc' ? 'desc' : 'asc';
  rows.sort(function(a, b) {{
    var av = a.cells[col].textContent.trim().toLowerCase();
    var bv = b.cells[col].textContent.trim().toLowerCase();
    var an = parseFloat(av), bn = parseFloat(bv);
    var cmp = (!isNaN(an) && !isNaN(bn)) ? an - bn : av.localeCompare(bv);
    return sortDir[col] === 'asc' ? cmp : -cmp;
  }});
  rows.forEach(function(r, i) {{
    tbody.appendChild(r);
    r.className = i % 2 === 0 ? 'row-even' : 'row-odd';
  }});
}}

// ---- Table Search ----
function filterTable(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('#fleet-table tbody tr').forEach(function(r) {{
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""

# ---------------------------------------------------------------------------
# 8. Save
# ---------------------------------------------------------------------------

def save_html(content: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    csv_path  = "fleet_status.csv"
    html_path = "fleet_dashboard.html"

    if not os.path.exists(csv_path):
        print(f"ERROR: '{csv_path}' not found.")
        return

    print("Reading fleet data…")
    devices = load_csv(csv_path)
    print(f"  Loaded {len(devices)} valid device records.")

    summary = calculate_summary(devices)
    print(f"  Summary: {summary}")

    print("Generating dashboard…")
    content = generate_dashboard(devices, summary)

    print(f"Writing '{html_path}'…")
    save_html(content, html_path)
    print(f"\nDone! Open '{html_path}' in any browser (internet required for map tiles).")

if __name__ == "__main__":
    main()
