import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import datetime

# ---- CONSTANTS ----
WATER_LPPD = 15          # liters per person per day (planning assumption)
LITERS_TO_GALLONS = 0.264172
SHELTER_FT2 = 40         # ft² per person in shelter (planning assumption)
MEALS_PER_DAY = 3
LOG_FILE = "population_needs_log.csv"

# States with higher de facto uplift
STATE_DEFECTO_UPLIFT = {
    "HI": 30,   # Hawaiʻi – tourism
    "NV": 25,   # Nevada – Vegas, Reno
    "FL": 20,   # Florida – tourism
    "CA": 10,   # California – commuters/visitors
    "NY": 10,   # New York
    "DC": 15    # Washington, D.C.
}

# For now we only need a slug for HI for you
STATE_SLUGS = {
    "HI": "hawaii",
    "NV": "nevada",
    "FL": "florida",
    "CA": "california",
    "NY": "new-york",
    "DC": "district-of-columbia",
}


# ---- CSV SETUP ----
def ensure_csv():
    """Create the CSV log with headers if it doesn't exist yet."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "city",
                "state",
                "resident_population",
                "extra_percent_for_defacto",
                "defacto_population",
                "shelter_percent",
                "water_liters",
                "water_gallons",
                "meals",
                "people_sheltered",
                "shelter_space_ft2"
            ])


# ---- SCRAPE POPULATION FROM CITY-SPECIFIC PAGE ----
def scrape_population_from_wpr(city, state):
    """
    Scrape population from a city-specific page like:
    https://worldpopulationreview.com/us-cities/hawaii/honolulu

    We:
      - Build the URL from state + city
      - Grab page text
      - Look for 'population of  344,098'
    """
    state_slug = STATE_SLUGS.get(state.upper())
    if not state_slug:
        print(f"[INFO] No state slug defined for {state}, skipping auto-scrape.")
        return None

    city_slug = city.strip().lower().replace(" ", "-")
    url = f"https://worldpopulationreview.com/us-cities/{state_slug}/{city_slug}"

    print(f"\n[INFO] Fetching {url}")
    try:
        html = requests.get(url, timeout=15).text
    except Exception as e:
        print(f"[ERROR] Could not fetch page: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # Look for 'population of  344,098'
    match = re.search(r"population of\s+([0-9,]+)", text, re.IGNORECASE)
    if not match:
        print("[WARN] Could not find 'population of <number>' in page text.")
        return None

    pop_str = match.group(1).replace(",", "")
    try:
        population = int(pop_str)
        print(f"[INFO] Found estimated resident population for {city}, {state}: {population:,}")
        return population
    except ValueError:
        print("[WARN] Matched number was not a valid integer.")
        return None


# ---- ESTIMATION LOGIC ----
def estimate_needs(de_facto, shelter_pct):
    water_liters = de_facto * WATER_LPPD
    water_gallons = water_lers = water_liters * LITERS_TO_GALLONS
    meals = de_facto * MEALS_PER_DAY

    people_sheltered = int(de_facto * (shelter_pct / 100.0))
    shelter_space = people_sheltered * SHELTER_FT2

    return {
        "water_liters": water_liters,
        "water_gallons": water_gallons,
        "meals": meals,
        "people_sheltered": people_sheltered,
        "shelter_space": shelter_space
    }


# ---- MAIN ----
def main():
    ensure_csv()

    print("=== DE FACTO POPULATION + NEEDS ESTIMATOR (US Cities by State) ===")

    city = input("\nCity name (e.g., Honolulu): ").strip()
    state = input("State abbreviation (e.g., HI, CA, FL): ").strip().upper()

    if not city or not state:
        print("City and state are required. Exiting.")
        return

    # Try scraping from city-specific page
    resident_pop = scrape_population_from_wpr(city, state)

    # Fallback if scraping didn't work
    if resident_pop is None:
        print("\n[!] Could not auto-detect population from worldpopulationreview.com.")
        try:
            # IMPORTANT: type ONLY numbers here, e.g. 344098
            resident_pop = int(input("Enter resident population manually (digits only): "))
        except ValueError:
            print("Invalid number entered (must be digits only). Exiting.")
            return

    # Determine extra de facto percentage
    default_extra = STATE_DEFECTO_UPLIFT.get(state)
    if default_extra is not None:
        print(f"\n[INFO] Using default de facto uplift of {default_extra}% for state {state}.")
        extra_pct = default_extra
    else:
        print("\nState not in predefined high de facto list.")
        print("You can enter your own planning uplift.")
        try:
            extra_pct = float(input("Percent above resident for de facto (e.g., 10): ") or 0)
        except ValueError:
            print("Invalid number entered. Exiting.")
            return

    # Shelter percentage
    try:
        shelter_pct = float(input("Percent of de facto needing shelter (e.g., 20): ") or 20)
    except ValueError:
        print("Invalid number entered. Exiting.")
        return

    de_facto = int(resident_pop * (1 + extra_pct / 100.0))
    estimates = estimate_needs(de_facto, shelter_pct)

    # ---- PRINT RESULTS ----
    print("\n====== RESULTS ======")
    print(f"City / State:                 {city}, {state}")
    print(f"Resident Population (WPR):    {resident_pop:,}")
    print(f"Extra % for De Facto:         {extra_pct:.1f}%")
    print("-----------------------------------------------")
    print(f"ESTIMATED DE FACTO POP:       {de_facto:,}")
    print("-----------------------------------------------")

    print("\n--- Daily Needs (Based on De Facto) ---")
    print(f"Water:                         {estimates['water_liters']:,} L "
          f"({estimates['water_gallons']:,} gal)")
    print(f"Meals:                         {estimates['meals']:,}")
    print(f"People Needing Shelter:        {estimates['people_sheltered']:,}")
    print(f"Shelter Floor Space:           {estimates['shelter_space']:,} ft²")

    # ---- APPEND TO CSV LOG ----
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            city,
            state,
            resident_pop,
            extra_pct,
            de_facto,
            shelter_pct,
            round(estimates["water_liters"], 2),
            round(estimates["water_gallons"], 2),
            round(estimates["meals"], 2),
            estimates["people_sheltered"],
            round(estimates["shelter_space"], 2),
        ])

    print(f"\n[INFO] Logged to {LOG_FILE}\n")


if __name__ == "__main__":
    main()