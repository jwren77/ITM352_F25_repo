# app.py
# Hawaii County Live EM Snapshot
# - Simple login
# - Uses hard-coded 2024 population for Hawaii County (Census table)
# - Pulls real-time-ish data from HCCDA / NOAA / NWS / FEMA
# - Shows a clean dashboard with charts
# - Exports a one-page PDF with logo, text summary, and charts

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
)
from datetime import datetime
from io import BytesIO
import os
import requests

import matplotlib
matplotlib.use("Agg")  # for servers with no display
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.pdfencrypt import StandardEncryption
from reportlab.lib.utils import ImageReader

app = Flask(__name__)

# ----------------------------------------------------
# Basic configuration
# ----------------------------------------------------

app.config["SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "dev-secret-key")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "hiema2025")

STATE_ABBR = "HI"
JURIS_LABEL = "Hawaii County"
SNAPSHOT_NAME = f"{JURIS_LABEL} Live Snapshot"

# Hard-coded population from your CO-EST2024-POP-15 table
HAWAII_COUNTY_POP_2024 = 209_790
POP_SOURCE_LABEL = "Hawaii County 2024 estimate (CO-EST2024-POP-15, Census)"

# FEMA open API
FEMA_API_URL = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"

# ArcGIS / NOAA / NWS services you gave
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

# ----------------------------------------------------
# Helper functions
# ----------------------------------------------------


def get_jurisdiction_population() -> tuple[int, str]:
    """
    For this project, just return the known 2024 population for Hawaii County.
    You already have the Census table; this keeps the app stable and simple.
    """
    return HAWAII_COUNTY_POP_2024, POP_SOURCE_LABEL


def get_fema_disaster_count_for_state(state_abbr: str) -> int:
    """
    Count FEMA disaster declarations for this state since 2000.
    Simple multi-hazard history indicator.
    """
    state_abbr = (state_abbr or "").upper()
    if not state_abbr:
        return 0

    flt = (
        f"state eq '{state_abbr}' and "
        f"incidentBeginDate ge '2000-01-01'"
    )
    params = {"$filter": flt, "$top": 1000}

    try:
        resp = requests.get(FEMA_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        records = data.get("DisasterDeclarationsSummaries", [])
        return len(records)
    except Exception:
        return 0


def get_arcgis_feature_count(base_url: str, where: str = "1=1") -> int:
    """
    Generic counter for ArcGIS FeatureServer layers.
    Uses returnCountOnly=true for speed.
    """
    if not base_url:
        return 0
    query_url = base_url.rstrip("/") + "/query"
    params = {
        "where": where,
        "returnCountOnly": "true",
        "f": "json",
    }
    try:
        resp = requests.get(query_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return int(data.get("count", 0))
    except Exception:
        return 0


def build_live_snapshot() -> dict:
    """
    Build a "what is happening now" snapshot for Hawaii County.

    All numbers are simple counts or planning assumptions.
    This is intentionally simple for a class project, not an official
    decision-support tool.
    """
    now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    juris_pop, pop_source = get_jurisdiction_population()

    # Planning assumptions: 30% affected, 20% of those need shelter
    population_affected = int(juris_pop * 0.30)
    estimated_shelter_need = int(population_affected * 0.20)
    total_shelter_capacity = 0  # unknown -> show gap only
    shelter_gap = estimated_shelter_need

    # Live counts from services
    volcano_sites = get_arcgis_feature_count(HAWAII_VOLCANO_STATUS_URL)
    water_shutoffs = get_arcgis_feature_count(HAWAII_WATER_SHUTOFF_URL)
    water_restrictions = get_arcgis_feature_count(HAWAII_WATER_RESTRICTION_URL)
    fire_events = get_arcgis_feature_count(HAWAII_FIRE_LOCATIONS_URL)
    shelters_layer_count = get_arcgis_feature_count(HAWAII_SHELTERS_URL)
    road_closures_live = get_arcgis_feature_count(HAWAII_ROAD_CLOSURES_URL)
    evacuation_features = get_arcgis_feature_count(HAWAII_EVACUATIONS_URL)
    noaa_metar_sites = get_arcgis_feature_count(NOAA_METAR_WIND_URL)
    nws_watch_warning_count = get_arcgis_feature_count(NWS_WATCHES_WARNINGS_URL)

    fema_disasters = get_fema_disaster_count_for_state(STATE_ABBR)

    # Simple "strain" score (just for visualization)
    strain_score = 0
    if estimated_shelter_need > 0:
        strain_score += 25
    if fire_events > 0:
        strain_score += 10
    if road_closures_live > 0:
        strain_score += 10
    if water_shutoffs > 0 or water_restrictions > 0:
        strain_score += 10
    if volcano_sites > 0:
        strain_score += 10
    if nws_watch_warning_count > 0:
        strain_score += 10
    if evacuation_features > 0:
        strain_score += 15

    strain_score = max(0, min(100, strain_score))
    if strain_score <= 30:
        strain_level = "Low"
    elif strain_score <= 60:
        strain_level = "Moderate"
    else:
        strain_level = "High"

    return {
        "snapshot_name": SNAPSHOT_NAME,
        "juris_label": JURIS_LABEL,
        "state_abbr": STATE_ABBR,
        "generated_at": now_utc,
        "juris_population": juris_pop,
        "population_source": pop_source,
        "population_affected": population_affected,
        "estimated_shelter_need": estimated_shelter_need,
        "total_shelter_capacity": total_shelter_capacity,
        "shelter_gap": shelter_gap,
        "volcano_sites": volcano_sites,
        "water_shutoffs": water_shutoffs,
        "water_restrictions": water_restrictions,
        "fire_events": fire_events,
        "shelters_layer_count": shelters_layer_count,
        "road_closures_live": road_closures_live,
        "evacuation_features": evacuation_features,
        "noaa_metar_sites": noaa_metar_sites,
        "nws_watch_warning_count": nws_watch_warning_count,
        "fema_disasters": fema_disasters,
        "strain_score": strain_score,
        "strain_level": strain_level,
    }


def wrap_text(text: str, max_chars: int = 90):
    """Very simple text wrapper for PDF paragraphs."""
    lines = []
    text = text or ""
    while text:
        lines.append(text[:max_chars])
        text = text[max_chars:]
    return lines


def find_logo_path():
    """
    Try a few common names in static/.
    If none is found, we just skip the logo in the PDF.
    """
    candidates = [
        "hiema_logo.png",
        "hiema_logo.jpg",
        "hiema_logo.jpeg",
        "hiema_logo.jfif",
    ]
    for name in candidates:
        path = os.path.join(app.root_path, "static", name)
        if os.path.exists(path):
            return path
    return None


def build_charts_images(snapshot: dict):
    """
    Build charts as PNG images in memory (BytesIO) using matplotlib.
    Returns two ImageReader objects: (hazard_img, weather_img).
    """

    # ---- Hazard / lifelines chart ----
    hazard_labels = [
        "Volcano",
        "Fire",
        "Road\nClosures",
        "Evacuations",
        "Shelters",
        "Water\nShut-offs",
        "Water\nRestrictions",
    ]
    hazard_values = [
        snapshot["volcano_sites"],
        snapshot["fire_events"],
        snapshot["road_closures_live"],
        snapshot["evacuation_features"],
        snapshot["shelters_layer_count"],
        snapshot["water_shutoffs"],
        snapshot["water_restrictions"],
    ]

    plt.figure(figsize=(6, 3))
    plt.bar(hazard_labels, hazard_values)
    plt.title("Hawaii County Hazards & Lifelines (HCCDA)")
    plt.ylabel("Feature count")
    plt.tight_layout()
    hazard_buf = BytesIO()
    plt.savefig(hazard_buf, format="png")
    plt.close()
    hazard_buf.seek(0)
    hazard_img = ImageReader(hazard_buf)

    # ---- Weather / alerts chart ----
    weather_labels = ["NOAA METAR Sites", "NWS Watches / Warnings"]
    weather_values = [
        snapshot["noaa_metar_sites"],
        snapshot["nws_watch_warning_count"],
    ]

    plt.figure(figsize=(4, 3))
    plt.bar(weather_labels, weather_values)
    plt.title("Weather & Alerts (NOAA / NWS)")
    plt.ylabel("Count")
    plt.tight_layout()
    weather_buf = BytesIO()
    plt.savefig(weather_buf, format="png")
    plt.close()
    weather_buf.seek(0)
    weather_img = ImageReader(weather_buf)

    return hazard_img, weather_img


def build_snapshot_pdf(snapshot: dict, encrypt: bool = False, pdf_password: str = "") -> BytesIO:
    """
    Build a one-page PDF snapshot with:
    - Clean header (logo right, title + timestamp left)
    - Population / FEMA context
    - Hazards & lifelines text
    - Strain text
    - Two charts (hazards + weather) in fixed space above the footer
    """
    buffer = BytesIO()

    if encrypt and pdf_password:
        enc = StandardEncryption(
            pdf_password,
            canPrint=1,
            canModify=0,
            canCopy=0,
            canAnnotate=0,
        )
        c = canvas.Canvas(buffer, pagesize=letter, encrypt=enc)
    else:
        c = canvas.Canvas(buffer, pagesize=letter)

    width, height = letter
    left = 50
    right = width - 50
    top = height - 50
    line_h = 14
    footer_y = 40  # a bit higher so we have space

    logo_path = find_logo_path()

    # ---------- HEADER ----------
    header_top = top - 10

    # Logo on top-right, a bit lower so it's clear of text
    if logo_path:
        c.drawImage(
            logo_path,
            right - 60,           # x
            header_top - 45,      # y
            width=60,
            height=60,
            preserveAspectRatio=True,
            mask="auto",
        )

    # Title + jurisdiction
    c.setFont("Helvetica-Bold", 17)
    c.drawString(left, header_top, f"{snapshot['juris_label']} – Live Snapshot")

    c.setFont("Helvetica-Bold", 11)
    c.drawString(left, header_top - 20, f"Jurisdiction: {snapshot['juris_label']} ({snapshot['state_abbr']})")
    c.drawString(left, header_top - 36, f"Title: {snapshot['snapshot_name']}")

    # Timestamp under the header, left side so it never touches the logo
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(left, header_top - 52, snapshot["generated_at"])

    # Start body text lower
    y = header_top - 80

    # ---------- 1. Population Context ----------
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "1. Population Context")
    c.line(left, y - 3, left + 260, y - 3)
    y -= line_h * 2
    c.setFont("Helvetica", 11)

    text1 = (
        f"Hawaii County population: {snapshot['juris_population']:,} "
        f"(source: {snapshot['population_source']})."
    )
    for line in wrap_text(text1):
        c.drawString(left, y, line)
        y -= line_h

    y -= line_h

    text2 = (
        f"Planning assumption: about 30% of the population "
        f"({snapshot['population_affected']:,} people) could be affected, "
        f"with roughly 20% of those ({snapshot['estimated_shelter_need']:,}) "
        f"potentially needing shelter support."
    )
    for line in wrap_text(text2):
        c.drawString(left, y, line)
        y -= line_h

    y -= line_h

    text3 = (
        f"FEMA has recorded approximately {snapshot['fema_disasters']} disaster "
        f"declarations for {snapshot['state_abbr']} since 2000 (multi-hazard)."
    )
    for line in wrap_text(text3):
        c.drawString(left, y, line)
        y -= line_h

    # ---------- 2. Hazards & Lifelines ----------
    y -= line_h * 2
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "2. Hazards & Lifelines (HCCDA / NOAA / NWS)")
    c.line(left, y - 3, left + 340, y - 3)
    y -= line_h * 2
    c.setFont("Helvetica", 11)

    bullets = [
        f"Volcano status features: {snapshot['volcano_sites']}",
        f"Fire location features: {snapshot['fire_events']}",
        f"Road closure features: {snapshot['road_closures_live']}",
        f"Evacuation features: {snapshot['evacuation_features']}",
        f"Emergency shelter features: {snapshot['shelters_layer_count']}",
        f"Water shut-off notices: {snapshot['water_shutoffs']}",
        f"Water conservation restriction notices: {snapshot['water_restrictions']}",
        f"NOAA METAR wind stations: {snapshot['noaa_metar_sites']}",
        f"NWS watches/warnings: {snapshot['nws_watch_warning_count']}",
    ]

    for b in bullets:
        for line in wrap_text("• " + b):
            c.drawString(left + 10, y, line)
            y -= line_h

    # ---------- 3. Strain Indicator ----------
    y -= line_h * 2
    c.setFont("Helvetica-Bold", 13)
    c.drawString(left, y, "3. Snapshot Strain Indicator")
    c.line(left, y - 3, left + 260, y - 3)
    y -= line_h * 2
    c.setFont("Helvetica", 11)

    text4 = (
        f"Overall strain indicator: {snapshot['strain_level']} "
        f"({snapshot['strain_score']}/100). This simple index considers "
        f"active hazards, closures, water restrictions, evacuation features, "
        f"and potential shelter demand."
    )
    for line in wrap_text(text4):
        c.drawString(left, y, line)
        y -= line_h

    # ---------- CHARTS (fixed positions so they never hit footer) ----------
    hazard_img, weather_img = build_charts_images(snapshot)

    # Weather chart sits just above footer
    weather_height = 80
    weather_width = (right - left) * 0.55
    weather_y = footer_y + 20  # bottom of weather chart
    c.drawImage(
        weather_img,
        left,
        weather_y,
        width=weather_width,
        height=weather_height,
        preserveAspectRatio=True,
        mask="auto",
    )

    # Hazard chart above weather
    hazard_height = 90
    hazard_width = right - left
    hazard_y = weather_y + weather_height + 15
    c.drawImage(
        hazard_img,
        left,
        hazard_y,
        width=hazard_width,
        height=hazard_height,
        preserveAspectRatio=True,
        mask="auto",
    )

    # ---------- FOOTER ----------
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        left,
        footer_y,
        "For training and planning use only. Sources: Census; FEMA OpenFEMA; "
        "HCCDA ArcGIS; NOAA METAR; NWS.",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ----------------------------------------------------
# Simple auth
# ----------------------------------------------------


@app.before_request
def require_login():
    """
    Require login for everything except /login and static files.
    """
    path = request.path
    if path.startswith("/static"):
        return
    if path not in ("/login",) and not session.get("logged_in"):
        return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid password."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ----------------------------------------------------
# Views
# ----------------------------------------------------


@app.route("/")
def dashboard():
    snapshot = build_live_snapshot()
    return render_template("dashboard.html", snapshot=snapshot)


@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    snapshot = build_live_snapshot()
    encrypt_flag = request.form.get("encrypt_pdf") == "on"
    pdf_password = request.form.get("pdf_password", "").strip()

    pdf_buffer = build_snapshot_pdf(snapshot, encrypt=encrypt_flag, pdf_password=pdf_password)
    filename = "Hawaii_County_Live_Snapshot.pdf"

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)