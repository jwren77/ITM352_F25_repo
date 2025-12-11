import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import datetime
import matplotlib.pyplot as plt

# Basic planning numbers
# Simple planning constants I use in the tool.
WATER_LPPD = 15          # liters per person per day
LITERS_TO_GALLONS = 0.264172
SHELTER_FT2 = 40         # square feet per person in shelter
MEALS_PER_DAY = 3

LOG_FILE = "population_needs_log.csv"
STATE_SLUG = "hawaii"    # This tool is focused on Hawaii cities

# Simple shelter site list
# I model some basic shelter sites for a few Hawaii cities.
SHELTER_SITES = {
    "Honolulu": [
        {"name": "Blaisdell Center", "capacity": 800},
        {"name": "McKinley High Gym", "capacity": 400},
    ],
    "Kahului": [
        {"name": "War Memorial Gym", "capacity": 600},
    ],
    "Hilo": [
        {"name": "Hilo High Gym", "capacity": 500},
    ],
}

# Hazard presets
# Hazard presets with different de facto uplift and shelter percent.
HAZARD_PRESETS = {
    "wildfire":  {"extra_pct": 10, "shelter_pct": 15},
    "hurricane": {"extra_pct": 5,  "shelter_pct": 25},
    "tsunami":   {"extra_pct": 0,  "shelter_pct": 40},
    "none":      {"extra_pct": 0,  "shelter_pct": 20},
}

# CSV helpers
def ensure_csv():
    """Make sure the CSV file exists with the right header."""
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "city",
                "hazard",
                "resident_population",
                "extra_percent_for_defacto",
                "defacto_population",
                "shelter_percent",
                "water_liters",
                "water_gallons",
                "meals",
                "people_sheltered",
                "shelter_space_ft2",
                "shelter_capacity_people",
                "shelter_shortfall",
                "water_capacity_gallons",
                "water_shortfall_gallons",
                "meal_capacity_per_day",
                "meal_shortfall",
                "evac_percent",
                "estimated_vehicles",
                "outbound_lanes",
                "road_capacity_vehicles_per_hour",
                "clearance_time_hours"
            ])


def append_to_csv(row):
    """Append one new row to the CSV log."""
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)



# Web scraping for population
def scrape_population_hawaii(city):
    """
    Scrape the population for a Hawaii city from WorldPopulationReview.
    Example URL: https://worldpopulationreview.com/us-cities/hawaii/honolulu
    """
    city_slug = city.strip().lower().replace(" ", "-")
    url = f"https://worldpopulationreview.com/us-cities/{STATE_SLUG}/{city_slug}"

    print(f"\n[INFO] Fetching {url}")
    try:
        html = requests.get(url, timeout=15).text
    except Exception as e:
        print(f"[ERROR] Could not fetch page: {e}")
        return None

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    # Look for text like "population of 344,098"
    match = re.search(r"population of\s+([0-9,]+)", text, re.IGNORECASE)
    if not match:
        print("[WARN] Could not find 'population of <number>' in page text.")
        return None

    pop_str = match.group(1).replace(",", "")
    try:
        population = int(pop_str)
        print(f"[INFO] Found estimated resident population for {city}: {population:,}")
        return population
    except ValueError:
        print("[WARN] Matched number was not a valid integer.")
        return None


# Hazard preset choice

def choose_hazard_preset():
    """Let me pick a hazard and return its preset values."""
    print("\nHazard options for Hawaii:")
    print("  1) Wildfire")
    print("  2) Hurricane")
    print("  3) Tsunami")
    print("  4) None / generic planning")

    choice = input("Choose hazard (1-4): ").strip()

    if choice == "1":
        hazard = "wildfire"
    elif choice == "2":
        hazard = "hurricane"
    elif choice == "3":
        hazard = "tsunami"
    else:
        hazard = "none"

    preset = HAZARD_PRESETS[hazard]
    print(f"[INFO] Using hazard preset: {hazard} "
          f"(extra de facto {preset['extra_pct']}%, shelter {preset['shelter_pct']}%)")
    return hazard, preset["extra_pct"], preset["shelter_pct"]


# Needs calculations
def estimate_needs(de_facto, shelter_pct):
    """Calculate daily water, meals, and shelter needs from de facto population."""
    water_liters = de_facto * WATER_LPPD
    water_gallons = water_liters * LITERS_TO_GALLONS
    meals = de_facto * MEALS_PER_DAY

    people_sheltered = int(de_facto * (shelter_pct / 100.0))
    shelter_space = people_sheltered * SHELTER_FT2

    return {
        "water_liters": water_liters,
        "water_gallons": water_gallons,
        "meals": meals,
        "people_sheltered": people_sheltered,
        "shelter_space": shelter_space,
    }


# Shelter capacity model
def estimate_shelter_capacity(city, resident_pop):
    """
    Estimate shelter capacity.
    If I have sites for the city, I sum them.
    Otherwise I assume 10% of resident population can be sheltered.
    """
    sites = SHELTER_SITES.get(city, [])
    if sites:
        capacity = sum(s["capacity"] for s in sites)
        print(f"[INFO] Using shelter sites model for {city}, total capacity {capacity} people.")
        return capacity
    else:
        capacity = int(resident_pop * 0.10)
        print(f"[INFO] No specific sites for {city}, assuming 10% of pop = {capacity} shelter spots.")
        return capacity


# Water and meals capability model
def estimate_water_and_meal_capacity():
    """
    Number of trucks, PODs, feeding sites and estimate capacities.
    This is more realistic than just guessing gallons and meals.
    """
    print("\nNow I enter rough resource capabilities for this area.")

    try:
        num_trucks = int(input("Number of water tanker trucks (about 4,000 gal each): ") or 0)
        num_pods = int(input("Number of POD sites operating: ") or 0)
        hours_pods_open = float(input("Hours PODs are open per day (e.g., 8): ") or 0)

        feeding_sites = int(input("Number of mass feeding sites: ") or 0)
    except ValueError:
        print("Invalid number entered. Exiting.")
        return None, None

    # Simple water capacity model
    truck_capacity_gal = num_trucks * 4000
    # POD: assume 250 vehicles/hour/lane, 10 gallons per vehicle, 1 lane per POD
    pod_capacity_gal = num_pods * 250 * 10 * hours_pods_open
    water_capacity_gallons = truck_capacity_gal + pod_capacity_gal

    # Simple meals capacity model
    meal_capacity_per_day = feeding_sites * 2000  # 2,000 meals per feeding site

    print(f"[INFO] Water capacity estimate: {water_capacity_gallons:,.0f} gal/day")
    print(f"[INFO] Meal capacity estimate: {meal_capacity_per_day:,} meals/day")

    return water_capacity_gallons, meal_capacity_per_day


# ======================
# Traffic model
# ======================
def estimate_traffic(de_facto):
    """
    Estimate vehicles and clearance time using simple traffic assumptions.
    """
    print("\nNow I estimate traffic and clearance time.")

    people_per_household = 2.5
    vehicles_per_household = 1.0

    try:
        evac_percent = float(input("Percent of de facto evacuating by car (e.g., 60): ") or 60)
        outbound_lanes = int(input("Number of outbound lanes available: ") or 1)
    except ValueError:
        print("Invalid traffic number. Exiting.")
        return None, None, None, None

    households = de_facto / people_per_household
    estimated_vehicles = int(households * vehicles_per_household * (evac_percent / 100.0))

    # Simple road capacity: 1,500 vehicles per lane per hour
    veh_per_lane_per_hour = 1500
    road_capacity_vehicles_per_hour = outbound_lanes * veh_per_lane_per_hour

    if road_capacity_vehicles_per_hour > 0:
        clearance_time_hours = estimated_vehicles / road_capacity_vehicles_per_hour
    else:
        clearance_time_hours = 0

    print(f"[INFO] Estimated vehicles evacuating: {estimated_vehicles:,}")
    print(f"[INFO] Road capacity: {road_capacity_vehicles_per_hour:,} veh/hour")
    print(f"[INFO] Clearance time: {clearance_time_hours:.2f} hours")

    return evac_percent, estimated_vehicles, outbound_lanes, road_capacity_vehicles_per_hour, clearance_time_hours


# ======================
# Shelter chart
# ======================
def make_shelter_need_vs_capacity_chart():
    """
    Make a simple chart comparing shelter need vs shelter capacity
    for each run in the CSV.
    """
    if not os.path.exists(LOG_FILE):
        print("[INFO] No CSV yet, skipping shelter chart.")
        return

    indices = []
    needs = []
    caps = []

    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        i = 0
        for row in reader:
            try:
                need = int(float(row["people_sheltered"]))
                cap = int(float(row["shelter_capacity_people"]))
            except (ValueError, KeyError):
                continue
            indices.append(i)
            needs.append(need)
            caps.append(cap)
            i += 1

    if not indices:
        print("[INFO] No data for shelter chart yet.")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(indices, needs, marker="o", label="Shelter need (people)")
    plt.plot(indices, caps, marker="x", label="Shelter capacity (people)")
    plt.xlabel("Run number")
    plt.ylabel("People")
    plt.title("Shelter need vs shelter capacity over runs")
    plt.legend()
    plt.tight_layout()
    chart_file = "shelter_need_vs_capacity.png"
    plt.savefig(chart_file)
    plt.close()
    print(f"[INFO] Saved shelter chart to {chart_file}")


# ======================
# Main program
# ======================
def main():
    ensure_csv()

    print("=== HAWAII DE FACTO POPULATION AND NEEDS TOOL (REALISTIC VERSION) ===")
    city = input("\nCity in Hawaii (e.g., Honolulu, Kahului, Hilo): ").strip()
    if not city:
        print("City is required. Exiting.")
        return

    # Try to scrape resident population
    resident_pop = scrape_population_hawaii(city)

    # If scraping fails, allow manual entry
    if resident_pop is None:
        print("\n[!] Could not auto-detect population from worldpopulationreview.com.")
        try:
            resident_pop = int(input("Enter resident population manually (digits only): "))
        except ValueError:
            print("Invalid number entered. Exiting.")
            return

    # Pick hazard preset
    hazard, extra_pct, default_shelter_pct = choose_hazard_preset()

    # Allow adjusting shelter percent if needed
    shelter_input = input(f"Shelter percent (default {default_shelter_pct}): ").strip()
    if shelter_input == "":
        shelter_pct = default_shelter_pct
    else:
        try:
            shelter_pct = float(shelter_input)
        except ValueError:
            print("Invalid shelter percent. Exiting.")
            return

    # Calculate de facto population
    de_facto = int(resident_pop * (1 + extra_pct / 100.0))

    # Estimate shelter capacity based on city and population
    shelter_capacity_people = estimate_shelter_capacity(city, resident_pop)

    # Water and meal capacity from trucks, PODs, and feeding sites
    water_capacity_gallons, meal_capacity_per_day = estimate_water_and_meal_capacity()
    if water_capacity_gallons is None:
        return

    # Traffic and clearance time
    evac_percent, estimated_vehicles, outbound_lanes, road_capacity_vph, clearance_time_hours = \
        estimate_traffic(de_facto)
    if evac_percent is None:
        return

    # Calculate needs
    needs = estimate_needs(de_facto, shelter_pct)

    # Compare needs vs capabilities
    shelter_shortfall = needs["people_sheltered"] - shelter_capacity_people
    water_shortfall_gal = needs["water_gallons"] - water_capacity_gallons
    meal_shortfall = needs["meals"] - meal_capacity_per_day

    # Print results
    print("\n====== RESULTS ======")
    print(f"City:                         {city}")
    print(f"Hazard:                       {hazard}")
    print(f"Resident population:          {resident_pop:,}")
    print(f"Extra percent for de facto:   {extra_pct:.1f}%")
    print("------------------------------------------")
    print(f"De facto population:          {de_facto:,}")
    print("------------------------------------------")
    print(f"Water need:                   {needs['water_liters']:,} L ({needs['water_gallons']:,} gal)")
    print(f"Meal need:                    {needs['meals']:,} meals/day")
    print(f"People needing shelter:       {needs['people_sheltered']:,}")
    print(f"Shelter space:                {needs['shelter_space']:,} ft^2")

    print("\n--- Capability vs Need ---")
    print(f"Shelter capacity (people):    {shelter_capacity_people:,}")
    print(f"Shelter need (people):        {needs['people_sheltered']:,}")
    print(f"Shelter shortfall:            {shelter_shortfall:,}")

    print(f"\nWater capacity (gal/day):     {water_capacity_gallons:,.0f}")
    print(f"Water need (gal/day):         {needs['water_gallons']:,.0f}")
    print(f"Water shortfall (gal):        {water_shortfall_gal:,.0f}")

    print(f"\nMeal capacity (meals/day):    {meal_capacity_per_day:,}")
    print(f"Meal need (meals/day):        {needs['meals']:,.0f}")
    print(f"Meal shortfall (meals):       {meal_shortfall:,.0f}")

    print(f"\nEvac percent by car:          {evac_percent:.1f}%")
    print(f"Estimated vehicles:           {estimated_vehicles:,}")
    print(f"Outbound lanes:               {outbound_lanes}")
    print(f"Road capacity (veh/hour):     {road_capacity_vph:,}")
    print(f"Clearance time (hours):       {clearance_time_hours:.2f}")

    # Save to CSV
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [
        timestamp,
        city,
        hazard,
        resident_pop,
        extra_pct,
        de_facto,
        shelter_pct,
        round(needs["water_liters"], 2),
        round(needs["water_gallons"], 2),
        round(needs["meals"], 2),
        needs["people_sheltered"],
        round(needs["shelter_space"], 2),
        shelter_capacity_people,
        shelter_shortfall,
        water_capacity_gallons,
        water_shortfall_gal,
        meal_capacity_per_day,
        meal_shortfall,
        round(evac_percent, 1),
        estimated_vehicles,
        outbound_lanes,
        road_capacity_vph,
        round(clearance_time_hours, 2),
    ]
    append_to_csv(row)
    print(f"\n[INFO] Logged to {LOG_FILE}")

    # Update shelter chart
    make_shelter_need_vs_capacity_chart()


if __name__ == "__main__":
    main()