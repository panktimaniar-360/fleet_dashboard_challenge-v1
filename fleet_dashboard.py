# fleet_dashboard_challenge-v1#!/usr/bin/env python3
"""
fleet_dashboard.py — SolidGPS Fleet Dashboard
Standard library only. Generates fleet_dashboard.html.
Fully responsive: mobile / tablet / desktop.
"""

import csv, json, os, sys
from datetime import datetime, timezone

CSV_FILE = "fleet_status.csv"
OUT_FILE = "fleet_dashboard.html"

STATUS_META = {
    "active":      {"label":"Active",      "color":"#22c55e","dot":"#16a34a"},
    "idle":        {"label":"Idle",        "color":"#f59e0b","dot":"#d97706"},
    "offline":     {"label":"Offline",     "color":"#6b7280","dot":"#4b5563"},
    "low_battery": {"label":"Low Battery", "color":"#ef4444","dot":"#dc2626"},
    "maintenance": {"label":"Maintenance", "color":"#3b82f6","dot":"#2563eb"},
    "unknown":     {"label":"Unknown",     "color":"#a855f7","dot":"#9333ea"},
}

AUSTRALIA_OUTLINE = [
    [113.338953,-25.671456],[114.160692,-21.844430],[114.532753,-22.341997],
    [115.597670,-20.703325],[118.396190,-20.263670],[121.889405,-19.169722],
    [122.222184,-18.197552],[124.459946,-19.009565],[128.128423,-14.999234],
    [129.122979,-14.918640],[129.391087,-14.391570],[130.339466,-14.380770],
    [130.183506,-14.898084],[130.617795,-14.097736],[131.826110,-12.240744],
    [132.560684,-11.603012],[135.924395,-11.618409],[136.258381,-12.049342],
    [136.492475,-11.857209],[136.951620,-12.351644],[136.685125,-12.887223],
    [136.305407,-13.291606],[135.961758,-13.324598],[136.077617,-13.724941],
    [137.689373,-13.949273],[138.213292,-14.178316],[138.338765,-14.671550],
    [139.141689,-14.802088],[139.520390,-15.189530],[139.792320,-15.064759],
    [141.055651,-16.832217],[141.630371,-16.736777],[141.748839,-17.543693],
    [140.817688,-17.381765],[140.843826,-17.847264],[141.073315,-18.161850],
    [141.388454,-18.163432],[141.467178,-19.048571],[141.562002,-19.279225],
    [141.702982,-19.183898],[142.160428,-19.046651],[142.360543,-18.768718],
    [142.836118,-18.394800],[143.074717,-18.268602],[143.477738,-18.248799],
    [143.581451,-18.082024],[144.165220,-18.280068],[144.516953,-18.600052],
    [144.581665,-18.860005],[145.324857,-19.019760],[145.588118,-19.498937],
    [145.867895,-19.680895],[147.063070,-19.315232],[148.043945,-19.658039],
    [148.281540,-19.769064],[148.883960,-20.375000],[149.126366,-20.666893],
    [149.267075,-21.150234],[149.482800,-21.311697],[149.512985,-21.715386],
    [149.940295,-22.464753],[150.457779,-22.550905],[150.553986,-23.010085],
    [150.795257,-23.425723],[151.184341,-23.893467],[151.448517,-24.147272],
    [151.909448,-24.071868],[152.361153,-24.255390],[152.538162,-24.699844],
    [152.714178,-25.206934],[153.142456,-26.126986],[153.161949,-26.641319],
    [153.092605,-27.260008],[153.569469,-28.110067],[153.512108,-28.995077],
    [153.339090,-29.459064],[153.069241,-29.836969],[152.891578,-30.338553],
    [152.453186,-31.048490],[151.709289,-31.969155],[152.171973,-32.163860],
    [152.133543,-32.456792],[151.830019,-32.680498],[151.386566,-33.189397],
    [151.012960,-33.723090],[151.202558,-33.978220],[150.902805,-34.278827],
    [150.365753,-35.671879],[150.073889,-36.420201],[149.946213,-37.109657],
    [149.997284,-37.425537],[149.423882,-37.772681],[148.304622,-37.809061],
    [147.381733,-38.219559],[146.922148,-38.606461],[146.318862,-38.608557],
    [145.489652,-38.524906],[145.098819,-38.097477],[144.882547,-37.824670],
    [145.032290,-37.611387],[144.485682,-36.700352],[143.505044,-36.666780],
    [143.038361,-36.060553],[142.178837,-35.656777],[141.605809,-35.156089],
    [140.727146,-35.062984],[140.000037,-34.984400],[139.992743,-34.484210],
    [139.519985,-34.077680],[139.086678,-33.903172],[138.484461,-33.855755],
    [137.939764,-33.378628],[137.371495,-32.896804],[136.531768,-31.880547],
    [135.824497,-31.179057],[135.346173,-30.226696],[135.003310,-29.533555],
    [134.272861,-29.283490],[134.198822,-29.016590],[132.990707,-28.666153],
    [132.301097,-28.396547],[131.704918,-28.315319],[129.000274,-28.272137],
    [128.999466,-28.999436],[128.999466,-31.000217],[128.999466,-33.999572],
    [127.805093,-33.878914],[127.274680,-33.926761],[126.596549,-34.022744],
    [125.688245,-33.897777],[125.041483,-33.882500],[124.221649,-33.928968],
    [123.659667,-33.891866],[122.811036,-33.914467],[122.183064,-33.931200],
    [121.298576,-33.821644],[120.580268,-33.930344],[119.893623,-33.976744],
    [119.298549,-33.946700],[119.183960,-33.994700],[118.997880,-34.005600],
    [117.793606,-34.464149],[117.319997,-33.963000],[116.625199,-33.963000],
    [115.833401,-33.854700],[115.517100,-32.900500],[115.005700,-32.219440],
    [114.596947,-31.439570],[114.224018,-30.201462],[114.069900,-29.463700],
    [113.477085,-28.287691],[113.338953,-27.215414],[113.338953,-25.671456]
]

TASMANIA_OUTLINE = [
    [144.005000,-39.978000],[144.476600,-40.078900],[145.000000,-40.792100],
    [145.454900,-41.070600],[146.000000,-41.000000],[146.814000,-41.190700],
    [147.748900,-41.059900],[148.296900,-42.079900],[148.326500,-42.396600],
    [148.035800,-42.820700],[147.555600,-42.855400],[147.042100,-43.185000],
    [146.534700,-43.511700],[146.191200,-43.548800],[145.693000,-43.218800],
    [145.404900,-42.743000],[145.233200,-42.083200],[144.693600,-41.418000],
    [144.273300,-40.981600],[144.005000,-40.452300],[144.005000,-39.978000]
]

def parse_float(v):
    try: return float(v)
    except: return None

def parse_battery(v):
    f = parse_float(v)
    return None if f is None else max(0, min(100, f))

def parse_last_seen(v):
    try:
        return datetime.strptime(v.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    except: return None

def time_ago(dt):
    if dt is None: return "Unknown"
    diff = datetime.now(timezone.utc) - dt
    if diff.total_seconds() < 0: return "Future timestamp"
    s = int(diff.total_seconds())
    if s < 60: return f"{s}s ago"
    if s < 3600: return f"{s//60}m ago"
    if s < 86400: return f"{s//3600}h {(s%3600)//60}m ago"
    return f"{s//86400}d {(s%86400)//3600}h ago"

def load_devices(path):
    devices = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            did = row.get("device_id","").strip()
            if not did: continue
            status = row.get("status","").strip().lower()
            if status not in STATUS_META: status = "unknown"
            lat = parse_float(row.get("lat",""))
            lon = parse_float(row.get("lon",""))
            valid = lat is not None and lon is not None and -44<=lat<=-10 and 113<=lon<=154
            last_dt = parse_last_seen(row.get("last_seen",""))
            devices.append({
                "id": did,
                "name": row.get("name","").strip() or did,
                "status": status,
                "battery": parse_battery(row.get("battery_pct","")),
                "lat": lat if valid else None,
                "lon": lon if valid else None,
                "time_ago": time_ago(last_dt),
                "location": row.get("location","").strip() or "Unknown",
                "has_coords": valid,
            })
    return devices

def generate_html(devices):
    counts = {}
    for d in devices:
        counts[d["status"]] = counts.get(d["status"], 0) + 1

    total        = len(devices)
    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")
    dj           = json.dumps(devices, default=str)
    smj          = json.dumps(STATUS_META)
    ausj         = json.dumps(AUSTRALIA_OUTLINE)
    tasj         = json.dumps(TASMANIA_OUTLINE)

    sum_cards = f'<div class="sc active-filter" data-status="all" onclick="setFilter(\'all\')"><div class="sc-dot" style="background:#94a3b8"></div><div class="sc-num">{total}</div><div class="sc-lbl">All</div></div>'
    for st, m in STATUS_META.items():
        c = counts.get(st, 0)
        if c == 0: continue
        sum_cards += f'<div class="sc" data-status="{st}" onclick="setFilter(\'{st}\')"><div class="sc-dot" style="background:{m["dot"]}"></div><div class="sc-num">{c}</div><div class="sc-lbl">{m["label"]}</div></div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>SolidGPS — Fleet Dashboard</title>
<style>
/* ── Reset & tokens ── */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0f1117;--s1:#1a1d27;--s2:#22263a;--bd:#2e3450;
  --tx:#e2e8f0;--mu:#94a3b8;--ac:#3b82f6;
  --r:10px;--hh:56px;--sh:58px;
  --font:'Inter',system-ui,-apple-system,sans-serif;
}}
html{{height:100%;-webkit-text-size-adjust:100%}}
body{{font-family:var(--font);background:var(--bg);color:var(--tx);font-size:14px;
      line-height:1.5;height:100%;overflow:hidden}}

/* ── Header ── */
.hdr{{
  height:var(--hh);display:flex;align-items:center;justify-content:space-between;
  padding:0 16px;background:var(--s1);border-bottom:1px solid var(--bd);
  flex-shrink:0;gap:8px;
}}
.hbrand{{display:flex;align-items:center;gap:10px;min-width:0}}
.hlogo{{width:32px;height:32px;background:var(--ac);border-radius:8px;display:flex;
        align-items:center;justify-content:center;font-weight:800;font-size:14px;
        color:#fff;flex-shrink:0}}
.htitle{{font-size:15px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.hsub{{font-size:11px;color:var(--mu);white-space:nowrap}}
.hmeta{{font-size:11px;color:var(--mu);text-align:right;flex-shrink:0;line-height:1.4}}

/* ── Summary strip ── */
.sumbar{{
  height:var(--sh);display:flex;align-items:center;gap:8px;
  padding:0 12px;background:var(--s1);border-bottom:1px solid var(--bd);
  overflow-x:auto;flex-shrink:0;-webkit-overflow-scrolling:touch;
  scrollbar-width:none;
}}
.sumbar::-webkit-scrollbar{{display:none}}
.sc{{
  display:flex;align-items:center;gap:7px;padding:7px 12px;
  background:var(--s2);border:1px solid var(--bd);border-radius:8px;
  cursor:pointer;white-space:nowrap;user-select:none;flex-shrink:0;
  transition:background .15s,border-color .15s;
  -webkit-tap-highlight-color:transparent;
}}
.sc:active,.sc:hover{{background:#2a2e45}}
.sc.active-filter{{border-color:var(--ac);background:#1e2a45}}
.sc-dot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.sc-num{{font-size:18px;font-weight:800;line-height:1}}
.sc-lbl{{font-size:11px;color:var(--mu);font-weight:500}}

/* ── App body (below header+sumbar) ── */
.app{{
  display:flex;flex-direction:column;
  height:calc(100dvh - var(--hh) - var(--sh));
  overflow:hidden;
}}

/* ── Tab bar (mobile only) ── */
.tabbar{{
  display:none;flex-shrink:0;
  background:var(--s1);border-bottom:1px solid var(--bd);
}}
.tabbar button{{
  flex:1;padding:10px 0;background:none;border:none;color:var(--mu);
  font-size:12px;font-weight:600;cursor:pointer;border-bottom:2px solid transparent;
  transition:.15s;-webkit-tap-highlight-color:transparent;
}}
.tabbar button.active{{color:var(--ac);border-color:var(--ac)}}

/* ── Desktop: side-by-side ── */
.content{{display:flex;flex:1;overflow:hidden}}

/* ── Panel (device list) ── */
.panel{{
  width:340px;flex-shrink:0;display:flex;flex-direction:column;
  background:var(--s1);border-right:1px solid var(--bd);overflow:hidden;
}}
.panel-hdr{{padding:12px 14px 10px;border-bottom:1px solid var(--bd);flex-shrink:0}}
.panel-hdr h2{{font-size:11px;font-weight:700;text-transform:uppercase;
               letter-spacing:.07em;color:var(--mu);margin-bottom:8px}}
.sbox{{
  display:flex;align-items:center;gap:6px;
  background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:0 10px;
}}
.sbox input{{
  background:none;border:none;outline:none;color:var(--tx);
  font-size:13px;padding:8px 6px;width:100%;
}}
.sbox input::placeholder{{color:var(--mu)}}
.sico{{color:var(--mu);flex-shrink:0}}

.dlist{{overflow-y:auto;flex:1;-webkit-overflow-scrolling:touch}}
.ditem{{
  display:flex;gap:11px;padding:11px 14px;
  border-bottom:1px solid var(--bd);cursor:pointer;
  transition:background .1s;position:relative;
  -webkit-tap-highlight-color:transparent;
}}
.ditem:active,.ditem:hover{{background:var(--s2)}}
.ditem.selected{{background:#1e2a45;border-left:3px solid var(--ac);padding-left:11px}}
.ditem.hidden{{display:none!important}}
.sdot{{width:10px;height:10px;border-radius:50%;margin-top:4px;flex-shrink:0}}
.sdot.pulse{{animation:pulse 2s ease-in-out infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.55}}}}
.dinfo{{flex:1;min-width:0}}
.dname{{font-size:13px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.did{{font-size:11px;color:var(--mu);margin-top:1px}}
.dmeta{{display:flex;gap:6px;margin-top:5px;align-items:center;flex-wrap:wrap}}
.stag{{font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;color:#fff}}
.nogps{{font-size:10px;color:var(--mu);font-style:italic}}
.batrow{{display:flex;align-items:center;gap:7px;margin-top:6px}}
.batbg{{flex:1;height:4px;background:var(--s2);border-radius:2px;overflow:hidden;min-width:40px}}
.batfill{{height:100%;border-radius:2px;transition:width .3s}}
.batlbl{{font-size:11px;color:var(--mu);white-space:nowrap;min-width:32px}}
.dlastseen{{font-size:11px;color:var(--mu);margin-top:3px}}
.nodevices{{padding:24px 16px;text-align:center;color:var(--mu);font-size:13px}}

/* ── Map ── */
.mapwrap{{flex:1;position:relative;background:#0d1520;overflow:hidden;min-height:0}}
#mapsvg{{width:100%;height:100%;display:block;touch-action:none}}

.mlegend{{
  position:absolute;top:10px;right:10px;
  background:rgba(26,29,39,.93);border:1px solid var(--bd);
  border-radius:8px;padding:9px 12px;font-size:11px;
  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  pointer-events:none;
}}
.mli{{display:flex;align-items:center;gap:7px;margin-bottom:4px;white-space:nowrap}}
.mli:last-child{{margin-bottom:0}}
.mldot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}

.tip{{
  position:absolute;background:var(--s1);border:1px solid var(--bd);
  border-radius:8px;padding:10px 13px;font-size:12px;
  display:none;z-index:20;min-width:170px;max-width:220px;
  box-shadow:0 8px 24px rgba(0,0,0,.6);pointer-events:none;line-height:1.6;
}}
.tip strong{{font-size:13px;display:block;margin-bottom:2px}}

.ncbar{{
  position:absolute;bottom:12px;left:50%;transform:translateX(-50%);
  background:rgba(15,17,23,.88);border:1px solid var(--bd);border-radius:20px;
  padding:5px 14px;font-size:11px;color:var(--mu);pointer-events:none;
  white-space:nowrap;display:none;
}}

/* ── Device detail sheet (mobile tap) ── */
.sheet{{
  display:none;position:fixed;bottom:0;left:0;right:0;z-index:30;
  background:var(--s1);border-top:1px solid var(--bd);border-radius:16px 16px 0 0;
  padding:16px;box-shadow:0 -8px 32px rgba(0,0,0,.5);
  transform:translateY(100%);transition:transform .25s cubic-bezier(.32,0,.2,1);
}}
.sheet.open{{transform:translateY(0)}}
.sheet-handle{{width:36px;height:4px;background:var(--bd);border-radius:2px;margin:0 auto 14px}}
.sheet-close{{position:absolute;top:12px;right:14px;background:none;border:none;
              color:var(--mu);font-size:20px;cursor:pointer;padding:4px;line-height:1}}
.sheet-name{{font-size:16px;font-weight:700;margin-bottom:2px}}
.sheet-id{{font-size:12px;color:var(--mu)}}
.sheet-grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px}}
.scard{{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:10px 12px}}
.scard-lbl{{font-size:11px;color:var(--mu);margin-bottom:3px}}
.scard-val{{font-size:15px;font-weight:700}}

/* ── Scrollbar ── */
::-webkit-scrollbar{{width:4px;height:4px}}
::-webkit-scrollbar-track{{background:var(--s1)}}
::-webkit-scrollbar-thumb{{background:var(--bd);border-radius:2px}}

/* ════════════════════════════════════════
   RESPONSIVE BREAKPOINTS
   ════════════════════════════════════════ */

/* Tablet: 481–900px — stack map on top, list below */
@media(max-width:900px) and (min-width:481px){{
  body{{overflow:hidden}}
  .content{{flex-direction:column}}
  .panel{{width:100%;border-right:none;border-top:1px solid var(--bd);
          height:260px;flex-shrink:0}}
  .mapwrap{{flex:1}}
  .hmeta .gen{{display:none}}
}}

/* Mobile: ≤480px — tabs switch between map and list */
@media(max-width:480px){{
  body{{overflow:hidden}}
  :root{{--hh:52px;--sh:52px}}
  .htitle{{font-size:14px}}
  .hsub{{display:none}}
  .hmeta{{display:none}}
  .sc-num{{font-size:15px}}
  .sc-lbl{{font-size:10px}}
  .sc{{padding:6px 10px;gap:5px}}

  .tabbar{{display:flex}}
  .content{{flex-direction:column;position:relative}}
  .panel{{
    width:100%;border-right:none;
    position:absolute;inset:0;z-index:2;
    transition:opacity .2s,transform .2s;
  }}
  .panel.tab-hidden{{opacity:0;pointer-events:none;transform:translateX(-8px)}}
  .mapwrap{{
    position:absolute;inset:0;z-index:1;
    transition:opacity .2s;
  }}
  .mapwrap.tab-hidden{{opacity:0;pointer-events:none}}
  .mlegend{{display:none}}
  .sheet{{display:block}}
}}
</style>
</head>
<body>

<!-- Header -->
<header class="hdr">
  <div class="hbrand">
    <div class="hlogo">SG</div>
    <div>
      <div class="htitle">Fleet Dashboard</div>
      <div class="hsub">SolidGPS — Australia Operations</div>
    </div>
  </div>
  <div class="hmeta">
    <div>{total} devices</div>
    <div class="gen">{generated_at}</div>
  </div>
</header>

<!-- Summary strip -->
<div class="sumbar">{sum_cards}</div>

<!-- App body -->
<div class="app">
  <!-- Tab bar (mobile) -->
  <div class="tabbar">
    <button id="tab-map" class="active" onclick="switchTab('map')">🗺 Map</button>
    <button id="tab-list" onclick="switchTab('list')">📋 Devices</button>
  </div>

  <div class="content">
    <!-- Device list panel -->
    <aside class="panel" id="panel">
      <div class="panel-hdr">
        <h2>Devices (<span id="visible-count">{total}</span>)</h2>
        <div class="sbox">
          <svg class="sico" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input id="search" type="search" placeholder="Name, ID or location…" oninput="applyFilters()" autocomplete="off">
        </div>
      </div>
      <div class="dlist" id="dlist"></div>
    </aside>

    <!-- Map -->
    <div class="mapwrap" id="mapwrap">
      <svg id="mapsvg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <filter id="glow"><feGaussianBlur stdDeviation="2" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="dropshadow"><feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="rgba(0,0,0,.7)"/></filter>
        </defs>
        <rect width="100%" height="100%" fill="#0d1520"/>
        <path id="aus-path" fill="#1a2b3c" stroke="#2a4a6a" stroke-width="1"/>
        <path id="tas-path" fill="#1a2b3c" stroke="#2a4a6a" stroke-width="1"/>
        <g id="city-labels"></g>
        <g id="markers"></g>
      </svg>
      <div class="mlegend">
        <div class="mli"><div class="mldot" style="background:#22c55e"></div>Active</div>
        <div class="mli"><div class="mldot" style="background:#f59e0b"></div>Idle</div>
        <div class="mli"><div class="mldot" style="background:#6b7280"></div>Offline</div>
        <div class="mli"><div class="mldot" style="background:#ef4444"></div>Low Battery</div>
        <div class="mli"><div class="mldot" style="background:#3b82f6"></div>Maintenance</div>
        <div class="mli"><div class="mldot" style="background:#a855f7"></div>Unknown</div>
      </div>
      <div class="tip" id="tip"></div>
      <div class="ncbar" id="ncbar"></div>
    </div>
  </div>
</div>

<!-- Mobile device detail sheet -->
<div class="sheet" id="sheet">
  <div class="sheet-handle"></div>
  <button class="sheet-close" onclick="closeSheet()">✕</button>
  <div class="sheet-name" id="sh-name"></div>
  <div class="sheet-id"   id="sh-id"></div>
  <div class="sheet-grid" id="sh-grid"></div>
</div>
<div id="sheet-backdrop" onclick="closeSheet()"
     style="display:none;position:fixed;inset:0;z-index:29;background:rgba(0,0,0,.4)"></div>

<script>
const DEVICES = {dj};
const STATUS_META = {smj};
const AUS = {ausj};
const TAS = {tasj};
const CITIES = [
  ["Sydney",       151.2093,-33.8688],["Melbourne",  144.9631,-37.8136],
  ["Brisbane",     153.0251,-27.4698],["Perth",      115.8575,-31.9505],
  ["Adelaide",     138.6007,-34.9285],["Hobart",     147.3272,-42.8821],
  ["Darwin",       130.8456,-12.4634],["Canberra",   149.1300,-35.2809],
  ["Alice Springs",133.8807,-23.6980],["Ballarat",   143.8503,-37.5622],
  ["Wollongong",   150.8931,-34.4278],["Cairns",     145.7781,-16.9203],
];

// ── Projection ───────────────────────────────────────────────────────────────
const LON0=113,LON1=154,LAT0=-44,LAT1=-10;
let W=800,H=500;
const PAD={{l:20,r:20,t:20,b:20}};

const merc = lat => Math.log(Math.tan(Math.PI/4 + lat*Math.PI/360));
const mMin = merc(LAT0), mMax = merc(LAT1);

function lx(lon){{ return PAD.l + (lon-LON0)/(LON1-LON0)*(W-PAD.l-PAD.r); }}
function ly(lat){{ return PAD.t + (mMax-merc(lat))/(mMax-mMin)*(H-PAD.t-PAD.b); }}
function path(pairs){{
  return pairs.map((p,i)=>`${{i?'L':'M'}}${{lx(p[0]).toFixed(1)}},${{ly(p[1]).toFixed(1)}}`).join(' ')+' Z';
}}

function syncSize(){{
  const svg=document.getElementById('mapsvg');
  const r=svg.getBoundingClientRect();
  if(r.width>10){{W=r.width;H=r.height;}}
}}

function drawMap(){{
  syncSize();
  document.getElementById('aus-path').setAttribute('d',path(AUS));
  document.getElementById('tas-path').setAttribute('d',path(TAS));

  const cg=document.getElementById('city-labels');
  cg.innerHTML='';
  // Hide city labels on very small maps
  if(W<300) return;
  CITIES.forEach(([name,lon,lat])=>{{
    const x=lx(lon),y=ly(lat);
    const dot=document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('cx',x);dot.setAttribute('cy',y);
    dot.setAttribute('r', W<500?1.5:2);dot.setAttribute('fill','#3d5a7a');
    cg.appendChild(dot);
    if(W>=400){{
      const t=document.createElementNS('http://www.w3.org/2000/svg','text');
      t.setAttribute('x',x+4);t.setAttribute('y',y+4);
      t.setAttribute('fill','#3d6090');
      t.setAttribute('font-size', W<600?'8':'10');
      t.setAttribute('font-family','system-ui');
      t.textContent=name;
      cg.appendChild(t);
    }}
  }});
  drawMarkers();
}}

// ── Device list ───────────────────────────────────────────────────────────────
function batCol(p){{
  if(p===null)return'#94a3b8';
  return p<=15?'#ef4444':p<=35?'#f59e0b':'#22c55e';
}}

function renderList(){{
  const ul=document.getElementById('dlist');
  DEVICES.forEach(d=>{{
    const m=STATUS_META[d.status]||STATUS_META['unknown'];
    const pulse=d.status==='active'?'pulse':'';
    const bp=d.battery;
    const el=document.createElement('div');
    el.className='ditem';
    el.dataset.id=d.id;
    el.dataset.status=d.status;
    el.dataset.q=(d.name+' '+d.id+' '+d.location).toLowerCase();
    el.innerHTML=`
      <div class="sdot ${{pulse}}" style="background:${{m.dot}}"></div>
      <div class="dinfo">
        <div class="dname">${{d.name}}</div>
        <div class="did">${{d.id}} · ${{d.location}}</div>
        <div class="dmeta">
          <span class="stag" style="background:${{m.color}}">${{m.label}}</span>
          ${{!d.has_coords?'<span class="nogps">⚠ No GPS</span>':''}}
        </div>
        <div class="batrow">
          <div class="batbg"><div class="batfill"
            style="width:${{bp!==null?bp:0}}%;background:${{batCol(bp)}}"></div></div>
          <span class="batlbl">${{bp!==null?bp+'%':'N/A'}}</span>
        </div>
        <div class="dlastseen">Last seen: ${{d.time_ago}}</div>
      </div>`;
    el.addEventListener('click',()=>onDeviceClick(d));
    ul.appendChild(el);
  }});
}}

// ── Filter ────────────────────────────────────────────────────────────────────
let curFilter='all';
function setFilter(s){{
  curFilter=s;
  document.querySelectorAll('.sc').forEach(c=>c.classList.toggle('active-filter',c.dataset.status===s));
  applyFilters();
}}
function applyFilters(){{
  const q=document.getElementById('search').value.toLowerCase().trim();
  let vis=0;
  document.querySelectorAll('.ditem').forEach(el=>{{
    const ok=(curFilter==='all'||el.dataset.status===curFilter)&&(!q||el.dataset.q.includes(q));
    el.classList.toggle('hidden',!ok);
    if(ok) vis++;
  }});
  document.getElementById('visible-count').textContent=vis;
  syncMarkerOpacity();
}}

// ── Select device ─────────────────────────────────────────────────────────────
function onDeviceClick(d){{
  selectItem(d.id);
  const mob=window.matchMedia('(max-width:480px)').matches;
  if(mob){{ openSheet(d); }}
  else{{ panToDevice(d); }}
}}

function selectItem(id){{
  document.querySelectorAll('.ditem').forEach(el=>el.classList.toggle('selected',el.dataset.id===id));
  const el=document.querySelector(`.ditem[data-id="${{id}}"]`);
  if(el) el.scrollIntoView({{behavior:'smooth',block:'nearest'}});
  // Highlight map marker
  document.querySelectorAll('.mk-ring,.mk-dot').forEach(m=>{{
    const sel=m.dataset.id===id;
    m.setAttribute('r', sel?(m.classList.contains('mk-ring')?13:7):(m.classList.contains('mk-ring')?9:5));
    m.setAttribute('stroke-width', sel?'2.5':'1.5');
  }});
}}

// ── Map markers ───────────────────────────────────────────────────────────────
function drawMarkers(){{
  const g=document.getElementById('markers');
  g.innerHTML='';
  const small=W<400;
  DEVICES.forEach(d=>{{
    if(!d.has_coords)return;
    const m=STATUS_META[d.status]||STATUS_META['unknown'];
    const x=lx(d.lon),y=ly(d.lat);
    const rr=small?7:9, rd=small?3.5:5;

    const ring=document.createElementNS('http://www.w3.org/2000/svg','circle');
    ring.setAttribute('cx',x);ring.setAttribute('cy',y);ring.setAttribute('r',rr);
    ring.setAttribute('fill',m.color+'22');ring.setAttribute('stroke',m.color);
    ring.setAttribute('stroke-width','1.5');
    ring.dataset.id=d.id;ring.classList.add('mk-ring');

    const dot=document.createElementNS('http://www.w3.org/2000/svg','circle');
    dot.setAttribute('cx',x);dot.setAttribute('cy',y);dot.setAttribute('r',rd);
    dot.setAttribute('fill',m.dot);dot.setAttribute('filter','url(#dropshadow)');
    dot.dataset.id=d.id;dot.classList.add('mk-dot');

    [ring,dot].forEach(el=>{{
      el.style.cursor='pointer';
      el.addEventListener('mouseenter',e=>showTip(d,e));
      el.addEventListener('mouseleave',hideTip);
      el.addEventListener('click',()=>onMarkerClick(d));
      // Touch
      el.addEventListener('touchend',e=>{{e.preventDefault();onMarkerClick(d);}},{{passive:false}});
    }});
    g.appendChild(ring);g.appendChild(dot);
  }});
  syncMarkerOpacity();
  updateNcBar();
}}

function onMarkerClick(d){{
  selectItem(d.id);
  const mob=window.matchMedia('(max-width:480px)').matches;
  if(mob){{ openSheet(d); switchTab('map'); }}
  else{{
    // scroll list item into view
    const el=document.querySelector(`.ditem[data-id="${{d.id}}"]`);
    if(el) el.scrollIntoView({{behavior:'smooth',block:'nearest'}});
  }}
}}

function panToDevice(d){{
  // On desktop/tablet, just highlight — map is static SVG
}}

function syncMarkerOpacity(){{
  const vis=new Set([...document.querySelectorAll('.ditem:not(.hidden)')].map(e=>e.dataset.id));
  document.querySelectorAll('.mk-ring,.mk-dot').forEach(el=>
    el.style.opacity=vis.has(el.dataset.id)?'1':'0.1');
}}

// ── Tooltip (desktop/tablet) ──────────────────────────────────────────────────
function showTip(d,e){{
  if(window.matchMedia('(max-width:480px)').matches)return;
  const m=STATUS_META[d.status]||STATUS_META['unknown'];
  const tip=document.getElementById('tip');
  tip.innerHTML=`<strong>${{d.name}}</strong>
    <span style="color:var(--mu)">${{d.id}}</span><br>
    <span style="color:${{m.color}};font-weight:600">${{m.label}}</span> · 🔋 ${{d.battery!==null?d.battery+'%':'N/A'}}<br>
    📍 ${{d.location}}<br>🕐 ${{d.time_ago}}`;
  tip.style.display='block';
  posTip(e);
}}
function hideTip(){{document.getElementById('tip').style.display='none';}}
document.addEventListener('mousemove',e=>{{
  const t=document.getElementById('tip');
  if(t.style.display==='block')posTip(e);
}});
function posTip(e){{
  const tip=document.getElementById('tip');
  const r=document.getElementById('mapwrap').getBoundingClientRect();
  let x=e.clientX-r.left+14,y=e.clientY-r.top+14;
  if(x+220>r.width)x-=240;
  if(y+140>r.height)y-=155;
  tip.style.left=x+'px';tip.style.top=y+'px';
}}

// ── No-coords bar ─────────────────────────────────────────────────────────────
function updateNcBar(){{
  const n=DEVICES.filter(d=>!d.has_coords).length;
  const bar=document.getElementById('ncbar');
  if(n>0){{bar.style.display='block';bar.textContent=`${{n}} device${{n>1?'s':''}} without GPS (not on map)`;}}
}}

// ── Mobile detail sheet ───────────────────────────────────────────────────────
function openSheet(d){{
  const m=STATUS_META[d.status]||STATUS_META['unknown'];
  document.getElementById('sh-name').textContent=d.name;
  document.getElementById('sh-id').textContent=d.id+' · '+d.location;
  const bp=d.battery;
  document.getElementById('sh-grid').innerHTML=`
    <div class="scard">
      <div class="scard-lbl">Status</div>
      <div class="scard-val" style="color:${{m.color}}">${{m.label}}</div>
    </div>
    <div class="scard">
      <div class="scard-lbl">Battery</div>
      <div class="scard-val" style="color:${{batCol(bp)}}">${{bp!==null?bp+'%':'N/A'}}</div>
    </div>
    <div class="scard" style="grid-column:1/-1">
      <div class="scard-lbl">Last Seen</div>
      <div class="scard-val" style="font-size:13px">${{d.time_ago}}</div>
    </div>
    ${{!d.has_coords?'<div class="scard" style="grid-column:1/-1"><div class="scard-lbl">GPS</div><div class="scard-val" style="font-size:13px;color:var(--mu)">No valid coordinates</div></div>':''}}
  `;
  document.getElementById('sheet').classList.add('open');
  document.getElementById('sheet-backdrop').style.display='block';
}}
function closeSheet(){{
  document.getElementById('sheet').classList.remove('open');
  document.getElementById('sheet-backdrop').style.display='none';
}}

// ── Tab switching (mobile) ────────────────────────────────────────────────────
function switchTab(tab){{
  const panel=document.getElementById('panel');
  const mapwrap=document.getElementById('mapwrap');
  if(tab==='map'){{
    panel.classList.add('tab-hidden');
    mapwrap.classList.remove('tab-hidden');
    document.getElementById('tab-map').classList.add('active');
    document.getElementById('tab-list').classList.remove('active');
    // Re-draw map in case size changed
    setTimeout(drawMap,50);
  }} else {{
    mapwrap.classList.add('tab-hidden');
    panel.classList.remove('tab-hidden');
    document.getElementById('tab-list').classList.add('active');
    document.getElementById('tab-map').classList.remove('active');
  }}
}}

// ── Resize ───────────────────────────────────────────────────────────────────
let resizeTimer;
window.addEventListener('resize',()=>{{
  clearTimeout(resizeTimer);
  resizeTimer=setTimeout(drawMap,120);
}});

// ── Init ──────────────────────────────────────────────────────────────────────
renderList();
// Use requestAnimationFrame to ensure layout is complete before reading SVG size
requestAnimationFrame(()=>requestAnimationFrame(drawMap));
</script>
</body>
</html>"""

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv)>1 else CSV_FILE
    if not os.path.exists(path):
        print(f"Error: '{path}' not found.", file=sys.stderr); sys.exit(1)
    devices = load_devices(path)
    print(f"Loaded {len(devices)} devices ({sum(1 for d in devices if d['has_coords'])} with valid coords)")
    html = generate_html(devices)
    with open(OUT_FILE,"w",encoding="utf-8") as f: f.write(html)
    print(f"Done → {OUT_FILE}  ({os.path.getsize(OUT_FILE)/1024:.1f} KB)")
