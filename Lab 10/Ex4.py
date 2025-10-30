# Read Json file of taxi trip data and create a df 
#calculate the median fare

import json
import pandas as pd

taxi_df = pd.read_json("Taxi_Trips.json")

#print a summary of the dataframe
print(taxi_df.describe())
print(taxi_df.head())

#print the median fare from the dataframe
print("Median Fare:", taxi_df['fare'].median())