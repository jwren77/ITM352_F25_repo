# Create a histogram from the trip miles data
import pandas as pd
import matplotlib.pyplot as plt

# Read the file and create a DataFrame
trips_df = pd.read_json('Trips from area 8.json')  
trip_miles_series = trips_df.trip_miles

# Create the histogram 
plt.hist(trip_miles_series)
plt.title('Distribution of Trip Miles')
plt.xlabel('Trip Miles')
plt.ylabel('Frequency')

plt.show()