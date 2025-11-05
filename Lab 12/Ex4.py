##Retrieve and analyze public vehicle license data from Chicago’s open API using sodapy and pandas. Use the the sodapy.Socrata client with the URL data.cityofchicago.org to get the JSON file rr23-ymwb. Set the limit to fetch only the first 500 records. This is data on passenger vehicle licenses. You will need to install sodapy.
#Extract vehicle license data from the city of Chicago's open data portal


import pandas as pd
from sodapy import Socrata

client = Socrata("data.cityofchicago.org", None)

#retrieve the JSON file for vehicle license data 
json_file = "rr23-ymwb"

results = client.get(json_file, limit=500)

#Convert to pandas DataFrame
df = pd.DataFrame.from_records(results)
print(df.head())

vehicles_and_fuel_sources = df[["public_vehicle_number", "vehicle_fuel_source"]]
print(f"\n Vehicles and Fuel Sources:\n {vehicles_and_fuel_sources}")

#group the vehicles and find totals by fuel source
vehicles_by_fuel_type  = vehicles_and_fuel_sources.groupby("vehicle_fuel_source").count()
print("\n Vehicles by Fuel Source:\n")
print(vehicles_by_fuel_type)