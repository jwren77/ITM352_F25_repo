import pandas as pd
import matplotlib.pyplot as plt

# Load data
trips_df = pd.read_json('Trips from area 8.json')

# Convert to numeric
trips_df['fare'] = pd.to_numeric(trips_df['fare'], errors='coerce')
trips_df['trip_miles'] = pd.to_numeric(trips_df['trip_miles'], errors='coerce')

# Drop rows with missing fare or miles
clean_df = trips_df.dropna(subset=['fare', 'trip_miles'])

# Filter out 0-mile trips AND trips < 2 miles
filtered_df = clean_df[(clean_df['trip_miles'] > 0) & (clean_df['trip_miles'] >= 2)]

# Scatter plot
plt.scatter(filtered_df['fare'], filtered_df['trip_miles'])
plt.title('Fare vs Trip Miles (Filtered)')
plt.xlabel('Fare ($)')
plt.ylabel('Trip Miles')

# Save the figure
plt.savefig('FaresXmiles.png')

# Also display it
plt.show()