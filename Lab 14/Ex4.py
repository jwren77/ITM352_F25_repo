import pandas as pd
import matplotlib.pyplot as plt

# Read the file
trips_df = pd.read_json('Trips_Fri07072017T4 trip_miles gt1.json')

# Drop rows with missing values in fare or tips
trips_df = trips_df.dropna(subset=['fare', 'tips'])

# Convert fare and tips to numeric (JSON often stores them as strings)
trips_df['fare'] = pd.to_numeric(trips_df['fare'], errors='coerce')
trips_df['tips'] = pd.to_numeric(trips_df['tips'], errors='coerce')

# Drop rows where conversion turned invalid values into NaN
trips_df = trips_df.dropna(subset=['fare', 'tips'])

# Create scatter plot
plt.scatter(trips_df['fare'], trips_df['tips'])

plt.title('Scatter Plot of Fare vs Tips')
plt.xlabel('Fare ($)')
plt.ylabel('Tips ($)')

plt.show()