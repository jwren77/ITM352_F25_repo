#Use the requests package to create a REST query that returns the count of licenses by driver_type. Here is the query that will retrieve this information and return a string of JSON 
#https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type

#Get a JSON file from the city of CHicagos data portal analyzedriver types 
#make use of SQL like capabilities of the portal

import requests
import pandas as pd

#Creat request query that returns the count of driver licenses by type

search_results = requests.get("https://data.cityofchicago.org/resource/97wa-y6ff.json?$select=driver_type,count(license)&$group=driver_type")
results_json = search_results.json()

#Convert the JSON string to a pandas DataFrame
results_df = pd.DataFrame.from_records(results_json)
results_df.columns = ['driver_type', 'count']
results_df = results_df.set_index('driver_type')

print("\n Driver Licenses by Type:\n")
print(results_df)