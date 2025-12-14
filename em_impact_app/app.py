# app.py
# HIEMA — Hawaii County Live Snapshot (training/demo)
# - Login + basic lockout
# - REAL population from Census ACS 2024 1-year (fallback to local)
# - Live-ish counts from your ArcGIS layers + OpenFEMA
# - Current weather (NWS) + active alerts (NWS)
# - Event type + severity changes impact assumptions + staffing recommendations
# - Dashboard auto-refresh via /api/snapshot
# - One-page PDF export (ReportLab canvas) that FITS and uses "Hawaii" (no okina) in PDF

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, send_file, jsonify
)
from datetime import datetime, timezone
from io import BytesIO
import os
import time
import math
import requests
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Encryption is optional; import path differs across reportlab versions
try:
    from reportlab.lib.pdfencrypt import StandardEncryption
except Exception:
    StandardEncryption = None  # gracefully disable

# -----------------------------
# App config
# -----------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "dev-secret-key")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "hiema2025")

# Cookie hardening (best when served over HTTPS)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=(os.getenv("FLASK_ENV") == "production"),
)

AGENCY_NAME = "HIEMA"  # per your request (no hyphen)
STATE_ABBR = "HI"
JURIS_LABEL = "Hawaiʻi County"      # dashboard can keep okina
PDF_JURIS_LABEL = "Hawaii County"   # PDF must be "Hawaii" (no okina)
SNAPSHOT_NAME = f"{JURIS_LABEL} Live Snapshot"

UA = {
    # NWS requires a UA with contact info. Put your email if you want.
    "User-Agent": "HIEMA-Snapshot/1.3 (training demo; contact: student@hawaii.edu)",
    "Accept": "application/geo+json, application/json;q=0.9, */*;q=0.8",
}

# -----------------------------
# Data sources
# -----------------------------
# Fallback population if Census fails
FALLBACK_POP_2024 = 209_790
FALLBACK_POP_SOURCE = "Fallback 2024 estimate (CO-EST2024-POP-15 / local table)"

# Census ACS 2024 1-year: B01003_001E total population
CENSUS_ACS_URL = "https://api.census.gov/data/2024/acs/acs1"
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY", "").strip()

# OpenFEMA
FEMA_API_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# ArcGIS services (yours)
HAWAII_VOLCANO_STATUS_URL = (
    "https://services.arcgis.com/uUvqNMGPm7axC2dD/arcgis/rest/services/"
    "Volcano_Status_Public/FeatureServer/0"
)
HAWAII_WATER_SHUTOFF_URL = (
    "https://services6.arcgis.com/5qY3CwWUmmseYeQN/arcgis/rest/services/"
    "Water_Shut_Off_Notice_view/FeatureServer/0"
)
HAWAII_WATER_RESTRICTION_URL = (
    "https://services6.arcgis.com/5qY3CwWUmmseYeQN/arcgis/rest/services/"
    "Water_Conservation_Restriction_Notices_view/FeatureServer/0"
)
HAWAII_FIRE_LOCATIONS_URL = (
    "https://services1.arcgis.com/C2LPusZs5OXNGFDn/arcgis/rest/services/"
    "Fire_Locations_(HCCDA)_Public/FeatureServer/0"
)
HAWAII_SHELTERS_URL = (
    "https://services1.arcgis.com/C2LPusZs5OXNGFDn/arcgis/rest/services/"
    "Emergency_Shelters_(HCCDA)_Public/FeatureServer/0"
)
HAWAII_ROAD_CLOSURES_URL = (
    "https://services1.arcgis.com/C2LPusZs5OXNGFDn/arcgis/rest/services/"
    "Road_Closures_(HCCDA)_Public/FeatureServer/0"
)
HAWAII_EVACUATIONS_URL = (
    "https://services1.arcgis.com/C2LPusZs5OXNGFDn/arcgis/rest/services/"
    "Evacuations_(HCCDA)_Public/FeatureServer/0"
)
NOAA_METAR_WIND_URL = (
    "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/"
    "NOAA_METAR_current_wind_speed_direction_v1/FeatureServer/0"
)
NWS_WATCHES_WARNINGS_URL = (
    "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/"
    "NWS_Watches_Warnings_v1/FeatureServer/6"
)

# Hawaii County Civil Defense Agency Hub (you requested this)
HCCDA_HUB = "https://hawaii-county-civil-defense-agency-hawaiicountygis.hub.arcgis.com"

# For NWS weather/alerts we use points near Hilo + Kailua-Kona
POINTS = {
    "Hilo": (19.707, -155.081),
    "Kailua-Kona": (19.639, -155.996),
}

# -----------------------------
# Tiny TTL cache
# -----------------------------
CACHE = {}  # key -> (expires_epoch, data)

def cache_get(key: str):
    rec = CACHE.get(key)
    if not rec:
        return None
    exp, data = rec
    return data if time.time() < exp else None

def cache_set(key: str, data, ttl_seconds: int = 120):
    CACHE[key] = (time.time() + ttl_seconds, data)

# -----------------------------
# Login lockout (demo-safe)
# -----------------------------
FAILED = {}  # key -> {"count": int, "locked_until": float}
MAX_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_SECONDS = int(os.getenv("LOCKOUT_SECONDS", "300"))

def client_key() -> str:
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown").split(",")[0].strip()
    ua = request.headers.get("User-Agent", "na")
    return f"{ip}|{ua[:60]}"

def is_locked(key: str):
    rec = FAILED.get(key)
    if not rec:
        return False, 0
    now = time.time()
    until = rec.get("locked_until", 0)
    if until > now:
        return True, int(until - now)
    rec["locked_until"] = 0
    return False, 0

def register_fail(key: str):
    rec = FAILED.setdefault(key, {"count": 0, "locked_until": 0})
    rec["count"] += 1
    if rec["count"] >= MAX_ATTEMPTS:
        rec["locked_until"] = time.time() + LOCKOUT_SECONDS

def clear_fails(key: str):
    FAILED[key] = {"count": 0, "locked_until": 0}

# -----------------------------
# Basic security headers
# -----------------------------
@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["Permissions-Policy"] = "geolocation=()"
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "font-src 'self' https://cdn.jsdelivr.net data:;"
    )
    return resp

# -----------------------------
# Auth gate
# -----------------------------
@app.before_request
def require_login():
    path = request.path
    if path.startswith("/static"):
        return
    if path in ("/login",):
        return
    # allow api snapshot to be protected too (keeps app simple)
    if not session.get("logged_in"):
        return redirect(url_for("login"))

# -----------------------------
# HTTP helpers
# -----------------------------
def http_get_json(url: str, params=None, timeout=12):
    r = requests.get(url, params=params, headers=UA, timeout=timeout)
    r.raise_for_status()
    return r.json()

def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def de_okina_for_pdf(s: str) -> str:
    # ONLY for PDF, as requested
    return (s or "").replace("ʻ", "").replace("’", "'").replace("ʻ", "").replace("Hawaiʻi", "Hawaii")

# -----------------------------
# Data: population
# -----------------------------
def get_jurisdiction_population() -> tuple[int, str]:
    """
    REAL population from Census ACS 2024 1-year:
    Hawaii County = state:15 county:001, variable B01003_001E
    """
    ck = "pop:hawaii_county_acs2024"
    cached = cache_get(ck)
    if cached:
        return cached["pop"], cached["source"]

    params = {
        "get": "NAME,B01003_001E",
        "for": "county:001",
        "in": "state:15",
    }
    if CENSUS_API_KEY:
        params["key"] = CENSUS_API_KEY

    try:
        data = http_get_json(CENSUS_ACS_URL, params=params, timeout=12)
        row = data[1]
        name = row[0]
        pop = int(float(row[1]))
        source = f"US Census ACS 2024 (acs1) B01003_001E – {name}"
        cache_set(ck, {"pop": pop, "source": source}, ttl_seconds=86400)
        return pop, source
    except Exception:
        return FALLBACK_POP_2024, FALLBACK_POP_SOURCE

# -----------------------------
# Data: FEMA count
# -----------------------------
def get_fema_disaster_count_for_state(state_abbr: str) -> int:
    state_abbr = (state_abbr or "").upper()
    if not state_abbr:
        return 0

    ck = f"fema_count:{state_abbr}"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    flt = f"state eq '{state_abbr}' and incidentBeginDate ge '2000-01-01'"
    params = {"$filter": flt, "$top": 1000}

    try:
        data = http_get_json(FEMA_API_URL, params=params, timeout=12)
        records = data.get("DisasterDeclarationsSummaries", [])
        count = len(records)
        cache_set(ck, count, ttl_seconds=3600)
        return count
    except Exception:
        return 0

# -----------------------------
# Data: ArcGIS feature counts
# -----------------------------
def get_arcgis_feature_count(base_url: str, where: str = "1=1") -> int:
    if not base_url:
        return 0

    ck = f"arc_count:{base_url}|{where}"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    query_url = base_url.rstrip("/") + "/query"
    params = {"where": where, "returnCountOnly": "true", "f": "json"}

    try:
        data = http_get_json(query_url, params=params, timeout=12)
        count = int(data.get("count", 0))
        cache_set(ck, count, ttl_seconds=120)
        return count
    except Exception:
        return 0

# -----------------------------
# Data: NWS current weather (observation)
# -----------------------------
def c_to_f(c):
    return (c * 9.0 / 5.0) + 32.0

def meters_per_sec_to_mph(ms):
    return ms * 2.236936

def parse_wind_speed(value):
    """
    NWS observation windSpeed is often a string like "20 mph" OR may be None.
    We'll keep it simple.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    # try to extract a number
    num = ""
    for ch in s:
        if ch.isdigit() or ch == ".":
            num += ch
        elif num:
            break
    try:
        return float(num) if num else None
    except Exception:
        return None

def get_nws_current_conditions(lat: float, lon: float) -> dict:
    """
    Uses api.weather.gov/points -> observationStations -> stations/{id}/observations/latest
    Returns: {temp_f, text, wind_mph, rh, obs_time}
    """
    ck = f"nws_obs:{lat:.3f},{lon:.3f}"
    cached = cache_get(ck)
    if cached:
        return cached

    out = {
        "temp_f": None,
        "text": None,
        "wind_mph": None,
        "rh": None,
        "obs_time": None,
        "station": None,
    }

    try:
        points = http_get_json(f"https://api.weather.gov/points/{lat},{lon}", timeout=12)
        stations_url = points["properties"]["observationStations"]
        stations = http_get_json(stations_url, timeout=12)
        feats = stations.get("features", [])
        if not feats:
            cache_set(ck, out, ttl_seconds=300)
            return out

        station_id = feats[0]["properties"].get("stationIdentifier") or feats[0]["id"].split("/")[-1]
        out["station"] = station_id

        obs = http_get_json(f"https://api.weather.gov/stations/{station_id}/observations/latest", timeout=12)
        p = obs.get("properties", {})

        temp_c = p.get("temperature", {}).get("value")
        if isinstance(temp_c, (int, float)):
            out["temp_f"] = round(c_to_f(temp_c), 1)

        rh = p.get("relativeHumidity", {}).get("value")
        if isinstance(rh, (int, float)):
            out["rh"] = int(round(rh))

        wind_ms = p.get("windSpeed", {}).get("value")
        # sometimes windSpeed.value is in m/s, sometimes None; fallback to text speed
        if isinstance(wind_ms, (int, float)):
            out["wind_mph"] = round(meters_per_sec_to_mph(wind_ms), 1)

        text = p.get("textDescription")
        out["text"] = text

        ts = p.get("timestamp")
        out["obs_time"] = ts

        cache_set(ck, out, ttl_seconds=300)  # 5 minutes
        return out
    except Exception:
        cache_set(ck, out, ttl_seconds=300)
        return out

# -----------------------------
# Data: NWS active alerts near a point
# -----------------------------
def get_nws_alerts_for_point(lat: float, lon: float) -> list[dict]:
    ck = f"nws_alerts:{lat:.3f},{lon:.3f}"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    alerts_out = []
    try:
        data = http_get_json("https://api.weather.gov/alerts/active", params={"point": f"{lat},{lon}"}, timeout=12)
        feats = data.get("features", [])
        for f in feats[:15]:
            p = f.get("properties", {})
            alerts_out.append({
                "id": f.get("id"),
                "headline": p.get("headline") or p.get("event"),
                "severity": p.get("severity"),
                "urgency": p.get("urgency"),
                "sent": p.get("sent"),
                "ends": p.get("ends") or p.get("expires"),
                "link": p.get("web"),
            })
        cache_set(ck, alerts_out, ttl_seconds=300)
        return alerts_out
    except Exception:
        cache_set(ck, alerts_out, ttl_seconds=300)
        return alerts_out

def merge_alerts(*lists):
    seen = set()
    out = []
    for lst in lists:
        for a in lst:
            aid = a.get("id") or a.get("headline")
            if not aid or aid in seen:
                continue
            seen.add(aid)
            out.append(a)
    # sort by sent desc when possible
    out.sort(key=lambda x: x.get("sent") or "", reverse=True)
    return out

# -----------------------------
# Data: Civil Defense updates (best-effort)
# -----------------------------
def fetch_hccda_updates() -> list[dict]:
    """
    ArcGIS Hub sites vary. We try a few common RSS-ish endpoints.
    If none work, returns [] and dashboard shows "No feed items".
    """
    ck = "hccda_feed"
    cached = cache_get(ck)
    if cached is not None:
        return cached

    candidates = [
        f"{HCCDA_HUB}/rss",
        f"{HCCDA_HUB}/feed",
        f"{HCCDA_HUB}/news/rss",
        f"{HCCDA_HUB}/pages/news?output=rss",
        f"{HCCDA_HUB}/pages/news?format=rss",
    ]

    for url in candidates:
        try:
            r = requests.get(url, headers=UA, timeout=12)
            if r.status_code != 200:
                continue
            txt = r.text.strip()
            if not txt:
                continue

            # XML RSS parse
            root = ET.fromstring(txt)
            items = []
            for it in root.findall(".//item")[:8]:
                title = (it.findtext("title") or "").strip()
                link = (it.findtext("link") or "").strip()
                pub = (it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date") or "").strip()
                if title:
                    items.append({"title": title, "link": link, "published": pub})
            if items:
                cache_set(ck, items, ttl_seconds=600)
                return items
        except Exception:
            continue

    cache_set(ck, [], ttl_seconds=600)
    return []

# -----------------------------
# Event modeling (training)
# -----------------------------
EVENT_PROFILES = {
    "baseline": {
        "label": "Event Baseline (Training Demo)",
        "affected_base": 0.10,
        "shelter_of_affected": 0.05,
        "staffing_factor": 0.8,
        "coa": [
            "Monitor/Inform: Push public info updates, validate reports, maintain situational awareness.",
            "Confirm road closures, shelter posture, and any evacuation areas with county products.",
        ]
    },
    "wildfire": {
        "label": "Wildfire",
        "affected_base": 0.30,
        "shelter_of_affected": 0.20,
        "staffing_factor": 1.2,
        "coa": [
            "Life safety: Verify evacuation zones, shelter openings, and road closure impacts.",
            "Lifelines: Prioritize power/water interruptions and access routes for responders.",
            "Public messaging: Fire/weather, air quality, shelter locations, re-entry guidance.",
        ]
    },
    "hurricane": {
        "label": "Hurricane / Tropical Storm",
        "affected_base": 0.40,
        "shelter_of_affected": 0.25,
        "staffing_factor": 1.35,
        "coa": [
            "Pre-impact: Stage resources, ensure shelter staffing/commodities, coordinate debris clearance planning.",
            "During: Maintain situational awareness, prioritize warnings and life safety, track closures.",
            "Post: Rapid damage assessment, prioritize lifeline restoration, resource requests.",
        ]
    },
    "flood": {
        "label": "Flood / Heavy Rain",
        "affected_base": 0.20,
        "shelter_of_affected": 0.10,
        "staffing_factor": 1.05,
        "coa": [
            "Confirm flood-prone routes, closures, and shelter needs; message high-water hazards.",
            "Coordinate with public works/roads; validate any rescues and shelter openings.",
        ]
    },
    "volcano": {
        "label": "Volcano / Lava / VOG",
        "affected_base": 0.15,
        "shelter_of_affected": 0.07,
        "staffing_factor": 1.0,
        "coa": [
            "Coordinate with USGS updates; identify affected zones and downwind VOG impacts.",
            "Plan for road closures, critical facility impacts, and protective action messaging.",
        ]
    },
}

def clamp(n, lo, hi):
    return max(lo, min(hi, n))

def compute_assumptions(pop: int, event: str, severity: int) -> dict:
    event = (event or "baseline").lower()
    severity = clamp(safe_int(severity, 3), 1, 5)

    prof = EVENT_PROFILES.get(event, EVENT_PROFILES["baseline"])
    # severity scales the base rates (gentle curve, not explosive)
    sev_mult = 0.7 + (severity * 0.15)  # sev=1->0.85, sev=5->1.45

    affected_pct = clamp(prof["affected_base"] * sev_mult, 0.01, 0.85)
    shelter_pct = clamp(prof["shelter_of_affected"] * sev_mult, 0.01, 0.60)

    affected = int(round(pop * affected_pct))
    shelter_need = int(round(affected * shelter_pct))

    return {
        "event_label": prof["label"],
        "affected_pct": affected_pct,
        "shelter_pct": shelter_pct,
        "affected": affected,
        "shelter_need": shelter_need,
        "staffing_factor": prof["staffing_factor"] * sev_mult,
        "coa": prof["coa"],
    }

def compute_strain(snapshot: dict, severity: int) -> tuple[int, str]:
    """
    Simple demo index: combines hazard counts + NWS alerts + severity.
    """
    s = 0
    s += severity * 8

    # hazard signals
    s += 8 if snapshot["fire_events"] > 0 else 0
    s += 8 if snapshot["road_closures_live"] > 0 else 0
    s += 6 if (snapshot["water_shutoffs"] > 0 or snapshot["water_restrictions"] > 0) else 0
    s += 6 if snapshot["volcano_sites"] > 0 else 0
    s += 10 if snapshot["evacuation_features"] > 0 else 0

    # NWS alerts are big EM signals
    s += min(18, 4 * len(snapshot.get("nws_alerts", [])))

    # shelter demand matters
    if snapshot["estimated_shelter_need"] >= 5000:
        s += 10
    elif snapshot["estimated_shelter_need"] >= 1000:
        s += 6
    elif snapshot["estimated_shelter_need"] > 0:
        s += 3

    score = clamp(s, 0, 100)
    level = "Low" if score <= 30 else ("Moderate" if score <= 60 else "High")
    return score, level

def recommend_eoc_and_staffing(strain_score: int, severity: int, staffing_factor: float) -> tuple[str, dict]:
    """
    Very practical, simple recommendation table.
    """
    # activation
    if strain_score <= 25 and severity <= 2:
        activation = "No EOC activation necessary"
        base_total = 0
    elif strain_score <= 55:
        activation = "Partial Activation"
        base_total = 12
    else:
        activation = "Full Activation"
        base_total = 24

    # staffing by section (only if activated)
    if base_total == 0:
        return activation, {
            "total": 0, "ops": 0, "plans": 0, "log": 0, "finance": 0, "pio": 0, "lno": 0
        }

    # scale and allocate
    scaled = int(round(base_total * staffing_factor))
    scaled = clamp(scaled, base_total, 40)

    ops = int(round(scaled * 0.38))
    plans = int(round(scaled * 0.22))
    log = int(round(scaled * 0.18))
    finance = int(round(scaled * 0.12))
    pio = int(round(scaled * 0.07))
    lno = max(0, scaled - (ops + plans + log + finance + pio))

    return activation, {
        "total": scaled, "ops": ops, "plans": plans, "log": log, "finance": finance, "pio": pio, "lno": lno
    }

# -----------------------------
# Snapshot builder
# -----------------------------
def build_live_snapshot(event: str = "baseline", severity: int = 3) -> dict:
    now_utc_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

    pop, pop_source = get_jurisdiction_population()
    assumptions = compute_assumptions(pop, event, severity)

    # ArcGIS / FEMA counts
    snap = {
        "agency": AGENCY_NAME,
        "snapshot_name": SNAPSHOT_NAME,
        "juris_label": JURIS_LABEL,
        "juris_label_pdf": PDF_JURIS_LABEL,  # for PDF only
        "state_abbr": STATE_ABBR,
        "generated_at": now_utc_iso,

        "event": (event or "baseline").lower(),
        "severity": clamp(safe_int(severity, 3), 1, 5),
        "event_label": assumptions["event_label"],

        "juris_population": pop,
        "population_source": pop_source,

        "population_affected": assumptions["affected"],
        "estimated_shelter_need": assumptions["shelter_need"],
        "affected_pct": assumptions["affected_pct"],
        "shelter_pct": assumptions["shelter_pct"],

        "volcano_sites": get_arcgis_feature_count(HAWAII_VOLCANO_STATUS_URL),
        "water_shutoffs": get_arcgis_feature_count(HAWAII_WATER_SHUTOFF_URL),
        "water_restrictions": get_arcgis_feature_count(HAWAII_WATER_RESTRICTION_URL),
        "fire_events": get_arcgis_feature_count(HAWAII_FIRE_LOCATIONS_URL),
        "shelters_layer_count": get_arcgis_feature_count(HAWAII_SHELTERS_URL),
        "road_closures_live": get_arcgis_feature_count(HAWAII_ROAD_CLOSURES_URL),
        "evacuation_features": get_arcgis_feature_count(HAWAII_EVACUATIONS_URL),
        "noaa_metar_sites": get_arcgis_feature_count(NOAA_METAR_WIND_URL),
        "nws_watch_warning_count": get_arcgis_feature_count(NWS_WATCHES_WARNINGS_URL),

        "fema_disasters": get_fema_disaster_count_for_state(STATE_ABBR),
    }

    # Weather
    weather = []
    for name, (lat, lon) in POINTS.items():
        obs = get_nws_current_conditions(lat, lon)
        weather.append({"name": name, **obs})
    snap["weather"] = weather

    # Alerts
    hilo_alerts = get_nws_alerts_for_point(*POINTS["Hilo"])
    kona_alerts = get_nws_alerts_for_point(*POINTS["Kailua-Kona"])
    snap["nws_alerts"] = merge_alerts(hilo_alerts, kona_alerts)[:6]

    # Civil defense updates
    snap["feed_items"] = fetch_hccda_updates()

    # Strain + staffing + COAs
    strain_score, strain_level = compute_strain(snap, snap["severity"])
    snap["strain_score"] = strain_score
    snap["strain_level"] = strain_level

    activation, staffing = recommend_eoc_and_staffing(
        strain_score=strain_score,
        severity=snap["severity"],
        staffing_factor=assumptions["staffing_factor"],
    )
    snap["eoc_recommendation"] = activation
    snap["staffing"] = staffing
    snap["coas"] = assumptions["coa"]

    # Situation summary (short, EM-style)
    snap["situation_summary"] = build_sit_summary(snap)

    # Recommended actions (short, actionable)
    snap["recommended_actions"] = build_recommended_actions(snap)

    return snap

def build_sit_summary(s: dict) -> str:
    # Quick EM summary that always populates
    bits = []
    bits.append(f"{s['event_label']} (Severity {s['severity']}/5).")
    if s.get("nws_alerts"):
        bits.append(f"{len(s['nws_alerts'])} active NWS alert(s) affecting points in Hawaii County.")
    if s.get("fire_events", 0) > 0:
        bits.append(f"Fire layer shows {s['fire_events']} feature(s).")
    if s.get("road_closures_live", 0) > 0:
        bits.append(f"Road closures layer shows {s['road_closures_live']} feature(s).")
    if s.get("evacuation_features", 0) > 0:
        bits.append(f"Evacuation layer shows {s['evacuation_features']} feature(s).")
    bits.append(f"Estimated affected: {s['population_affected']:,}; shelter need: {s['estimated_shelter_need']:,}.")
    bits.append(f"Strain: {s['strain_level']} ({s['strain_score']}/100).")
    return " ".join(bits)

def build_recommended_actions(s: dict) -> list[str]:
    actions = []
    # Always include message discipline
    actions.append("Confirm current protective actions (evacuation/shelter posture) and publish a concise public update.")
    # Weather/alerts
    if s.get("nws_alerts"):
        actions.append("Review active NWS alerts and align messaging (timing, impacted areas, safety actions).")
    # Lifelines
    if s.get("road_closures_live", 0) > 0:
        actions.append("Coordinate with roads/public works on closure impacts and access routes for response.")
    if s.get("water_shutoffs", 0) > 0 or s.get("water_restrictions", 0) > 0:
        actions.append("Assess water system impacts/restrictions and identify critical facilities affected.")
    # EOC posture
    if s.get("eoc_recommendation") != "No EOC activation necessary":
        actions.append(f"Implement {s['eoc_recommendation']} and staff core sections (Ops/Plans/Log) for the next operational period.")
    else:
        actions.append("Maintain monitoring posture; prepare escalation triggers if conditions worsen.")
    return actions[:6]

# -----------------------------
# Charts (matplotlib -> ImageReader for canvas.drawImage)
# -----------------------------
def build_chart_images(snapshot: dict):
    # 1) Hazards bar
    labels = ["Volcano", "Fire", "Road\nClosures", "Evac", "Shelters", "Water\nShut", "Water\nRestr"]
    vals = [
        snapshot["volcano_sites"],
        snapshot["fire_events"],
        snapshot["road_closures_live"],
        snapshot["evacuation_features"],
        snapshot["shelters_layer_count"],
        snapshot["water_shutoffs"],
        snapshot["water_restrictions"],
    ]

    plt.figure(figsize=(7.0, 2.3))
    plt.bar(labels, vals)
    plt.title("Hazards & Lifelines (HCCDA Live Counts)")
    plt.ylabel("Count")
    plt.tight_layout()
    b1 = BytesIO()
    plt.savefig(b1, format="png", dpi=180)
    plt.close()
    b1.seek(0)
    img_haz = ImageReader(b1)

    # 2) Impact chart (affected vs shelter need)
    plt.figure(figsize=(3.4, 2.3))
    plt.bar(["Affected", "Shelter Need"], [snapshot["population_affected"], snapshot["estimated_shelter_need"]])
    plt.title("Estimated Impact (Assumptions)")
    plt.tight_layout()
    b2 = BytesIO()
    plt.savefig(b2, format="png", dpi=180)
    plt.close()
    b2.seek(0)
    img_imp = ImageReader(b2)

    return img_haz, img_imp

# -----------------------------
# PDF generator (canvas) — NO Platypus, so no LayoutError
# -----------------------------
def find_logo_path():
    for name in ["hiema_logo.png", "hiema_logo.jpg", "hiema_logo.jpeg", "hiema_logo.jfif"]:
        path = os.path.join(app.root_path, "static", name)
        if os.path.exists(path):
            return path
    return None

def draw_wrapped(c, text, x, y, max_width, font="Helvetica", size=9.5, leading=12):
    """
    Wrap by word and draw. Returns new y.
    """
    c.setFont(font, size)
    words = (text or "").split()
    line = ""
    for w in words:
        test = (line + " " + w).strip()
        if c.stringWidth(test, font, size) <= max_width:
            line = test
        else:
            c.drawString(x, y, test if not line else line)
            y -= leading
            line = w
    if line:
        c.drawString(x, y, line)
        y -= leading
    return y

def build_snapshot_pdf(snapshot: dict, encrypt: bool = False, pdf_password: str = "") -> BytesIO:
    buf = BytesIO()

    # Optional encryption
    if encrypt and pdf_password and StandardEncryption:
        enc = StandardEncryption(pdf_password, canPrint=1, canModify=0, canCopy=0, canAnnotate=0)
        c = canvas.Canvas(buf, pagesize=letter, encrypt=enc)
    else:
        c = canvas.Canvas(buf, pagesize=letter)

    W, H = letter
    margin = 36
    left = margin
    right = W - margin
    top = H - margin
    bottom = margin

    # PDF must say Hawaii (no okina)
    juris_pdf = snapshot.get("juris_label_pdf") or PDF_JURIS_LABEL

    # Header
    logo = find_logo_path()
    if logo:
        c.drawImage(logo, right - 58, top - 52, width=52, height=52, preserveAspectRatio=True, mask="auto")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(left, top, f"{AGENCY_NAME} — {de_okina_for_pdf(juris_pdf)} Live Snapshot")

    c.setFont("Helvetica", 9.5)
    c.drawString(left, top - 14, f"Generated (UTC): {snapshot['generated_at']}")
    c.drawString(left, top - 26, f"Event: {snapshot['event_label']}  |  Severity: {snapshot['severity']}/5")
    c.drawString(left, top - 38, f"Strain (demo index): {snapshot['strain_level']} ({snapshot['strain_score']}/100)")
    c.drawString(left, top - 50, f"EOC Recommendation: {snapshot['eoc_recommendation']}")

    y = top - 66

    # Two-column layout zones (top half)
    col_gap = 12
    col_w = (right - left - col_gap) / 2
    x1 = left
    x2 = left + col_w + col_gap

    # Left column: Operational summary + hazards table
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x1, y, "Operational Summary")
    y1 = y - 12

    pop_line = f"Population: {snapshot['juris_population']:,}"
    aff_line = f"Affected (assumption): {snapshot['population_affected']:,}  ({snapshot['affected_pct']*100:.1f}%)"
    shl_line = f"Shelter need (assumption): {snapshot['estimated_shelter_need']:,}  ({snapshot['shelter_pct']*100:.1f}% of affected)"
    src_line = f"Population source: {de_okina_for_pdf(snapshot['population_source'])}"
    fema_line = f"FEMA declarations since 2000 ({snapshot['state_abbr']}): {snapshot['fema_disasters']}"

    c.setFont("Helvetica", 9.5)
    for line in [pop_line, aff_line, shl_line, fema_line]:
        c.drawString(x1, y1, line)
        y1 -= 12

    y1 = draw_wrapped(c, src_line, x1, y1, max_width=col_w, font="Helvetica", size=8.6, leading=10)

    # Hazards table
    y1 -= 6
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x1, y1, "Hazards & Lifelines (HCCDA Live Counts)")
    y1 -= 12

    rows = [
        ("Volcano status features", snapshot["volcano_sites"]),
        ("Fire location features", snapshot["fire_events"]),
        ("Road closure features", snapshot["road_closures_live"]),
        ("Evacuation features", snapshot["evacuation_features"]),
        ("Emergency shelter features", snapshot["shelters_layer_count"]),
        ("Water shut-off notices", snapshot["water_shutoffs"]),
        ("Water restriction notices", snapshot["water_restrictions"]),
    ]

    c.setFont("Helvetica-Bold", 9.2)
    c.drawString(x1, y1, "Metric")
    c.drawRightString(x1 + col_w, y1, "Count")
    y1 -= 8
    c.line(x1, y1, x1 + col_w, y1)
    y1 -= 10

    c.setFont("Helvetica", 9.2)
    for label, val in rows:
        c.drawString(x1, y1, de_okina_for_pdf(label))
        c.drawRightString(x1 + col_w, y1, str(val))
        y1 -= 11

    # Right column: Weather + alerts + feed
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x2, y, "Current Weather (NWS)")
    y2 = y - 12

    c.setFont("Helvetica", 9.2)
    for w in snapshot.get("weather", []):
        name = de_okina_for_pdf(w.get("name") or "Site")
        tf = w.get("temp_f")
        txt = w.get("text") or "—"
        wind = w.get("wind_mph")
        rh = w.get("rh")
        obs = w.get("obs_time") or "—"
        line1 = f"{name}: {('%.1f' % tf) if isinstance(tf, (int, float)) else '—'}°F, {de_okina_for_pdf(txt)}"
        line2 = f"Wind: {('%.1f' % wind) if isinstance(wind, (int, float)) else '—'} mph  |  RH: {rh if rh is not None else '—'}%  |  Obs: {obs}"
        y2 = draw_wrapped(c, line1, x2, y2, col_w, font="Helvetica", size=9.2, leading=11)
        y2 = draw_wrapped(c, line2, x2, y2, col_w, font="Helvetica", size=8.6, leading=10)
        y2 -= 4

    y2 -= 4
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x2, y2, "Most Recent NWS Alerts (Active)")
    y2 -= 12

    alerts = snapshot.get("nws_alerts", [])
    if not alerts:
        c.setFont("Helvetica", 9.2)
        c.drawString(x2, y2, "No active alerts returned for county points.")
        y2 -= 12
    else:
        c.setFont("Helvetica", 8.8)
        for a in alerts[:3]:
            hl = de_okina_for_pdf(a.get("headline") or "Alert")
            sev = a.get("severity") or "—"
            urg = a.get("urgency") or "—"
            ends = a.get("ends") or "—"
            y2 = draw_wrapped(c, f"• {hl}", x2, y2, col_w, font="Helvetica", size=8.8, leading=10)
            y2 = draw_wrapped(c, f"  Severity: {sev}  |  Urgency: {urg}  |  Ends/Expires: {ends}", x2, y2, col_w, font="Helvetica", size=8.1, leading=9.5)
            y2 -= 2

    y2 -= 2
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x2, y2, "Hawaii County Civil Defense Updates (Hub)")
    y2 -= 12

    feed = snapshot.get("feed_items", [])
    c.setFont("Helvetica", 8.8)
    if not feed:
        c.drawString(x2, y2, "No feed items retrieved at this time.")
        y2 -= 10
    else:
        for it in feed[:3]:
            title = de_okina_for_pdf(it.get("title") or "Update")
            pub = de_okina_for_pdf(it.get("published") or "")
            y2 = draw_wrapped(c, f"• {title}", x2, y2, col_w, font="Helvetica", size=8.8, leading=10)
            if pub:
                y2 = draw_wrapped(c, f"  {pub}", x2, y2, col_w, font="Helvetica", size=8.1, leading=9.5)
            y2 -= 2

    # Middle: Situation summary + actions + staffing (full width)
    y_mid = min(y1, y2) - 8
    y_mid = max(y_mid, bottom + 230)  # reserve space for charts

    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y_mid, "Situation Summary")
    y_mid -= 12
    y_mid = draw_wrapped(c, de_okina_for_pdf(snapshot.get("situation_summary", "")), left, y_mid, right - left, font="Helvetica", size=9.3, leading=11)

    y_mid -= 6
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y_mid, "Recommended Actions (Next Operational Period)")
    y_mid -= 12
    c.setFont("Helvetica", 9.3)
    for act in snapshot.get("recommended_actions", [])[:5]:
        y_mid = draw_wrapped(c, f"• {de_okina_for_pdf(act)}", left, y_mid, right - left, font="Helvetica", size=9.3, leading=11)

    # Staffing line
    y_mid -= 4
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, y_mid, "EOC Staffing (Recommendation)")
    y_mid -= 12

    st = snapshot.get("staffing", {})
    c.setFont("Helvetica", 9.3)
    c.drawString(left, y_mid, f"{snapshot['eoc_recommendation']}  —  Total: {st.get('total', 0)}")
    y_mid -= 12
    c.setFont("Helvetica", 9.0)
    c.drawString(left, y_mid, f"Ops: {st.get('ops',0)}   Plans: {st.get('plans',0)}   Log: {st.get('log',0)}   Finance: {st.get('finance',0)}   PIO: {st.get('pio',0)}   LNO: {st.get('lno',0)}")
    y_mid -= 10

    # Charts area (bottom)
    img_haz, img_imp = build_chart_images(snapshot)
    chart_y = bottom + 18
    haz_h = 155
    haz_w = (right - left) * 0.66
    imp_w = (right - left) - haz_w - 10
    imp_h = 155

    c.drawImage(img_haz, left, chart_y, width=haz_w, height=haz_h, preserveAspectRatio=True, mask="auto")
    c.drawImage(img_imp, left + haz_w + 10, chart_y, width=imp_w, height=imp_h, preserveAspectRatio=True, mask="auto")

    # Footer
    c.setFont("Helvetica-Oblique", 7.7)
    c.drawString(
        left,
        bottom,
        "Training/demo only. Sources: US Census (ACS), OpenFEMA, HCCDA ArcGIS layers, NWS API, Hawaii County Civil Defense Hub (best-effort feed)."
    )

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

# -----------------------------
# Routes
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    key = client_key()

    locked, remaining = is_locked(key)
    if locked:
        return render_template("login.html", error=f"Too many attempts. Try again in {remaining} seconds.")

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == APP_PASSWORD:
            clear_fails(key)
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        register_fail(key)
        locked, remaining = is_locked(key)
        error = f"Too many attempts. Try again in {remaining} seconds." if locked else "Invalid password."

    return render_template("login.html", error=error)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def dashboard():
    event = request.args.get("event", "baseline")
    severity = safe_int(request.args.get("severity", 3), 3)
    snapshot = build_live_snapshot(event=event, severity=severity)
    return render_template("dashboard.html", snapshot=snapshot)

@app.route("/api/snapshot")
def api_snapshot():
    event = request.args.get("event", "baseline")
    severity = safe_int(request.args.get("severity", 3), 3)

    ck = f"snapshot:{event}:{severity}"
    cached = cache_get(ck)
    if cached:
        return jsonify(cached)

    snap = build_live_snapshot(event=event, severity=severity)
    cache_set(ck, snap, ttl_seconds=60)  # 1 min feels live without hammering APIs
    return jsonify(snap)

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    event = request.form.get("event", "baseline")
    severity = safe_int(request.form.get("severity", 3), 3)

    encrypt_flag = request.form.get("encrypt_pdf") == "on"
    pdf_password = (request.form.get("pdf_password", "") or "").strip()

    snap = build_live_snapshot(event=event, severity=severity)
    pdf_buffer = build_snapshot_pdf(snap, encrypt=encrypt_flag, pdf_password=pdf_password)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="Hawaii_County_Live_Snapshot.pdf",
        mimetype="application/pdf",
    )

if __name__ == "__main__":
    app.run(debug=True)