import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load the data
trips_df = pd.read_json('Trips from area 8.json')

# Convert numeric columns
trips_df['fare'] = pd.to_numeric(trips_df['fare'], errors='coerce')
trips_df['trip_miles'] = pd.to_numeric(trips_df['trip_miles'], errors='coerce')
trips_df['dropoff_community_area'] = pd.to_numeric(trips_df['dropoff_community_area'], errors='coerce')

# Drop rows missing any of the three values
clean_df = trips_df.dropna(subset=['fare', 'trip_miles', 'dropoff_community_area'])

# Setup 3D figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create 3D scatter plot
ax.scatter(
    clean_df['fare'],
    clean_df['trip_miles'],
    clean_df['dropoff_community_area'],
    c='blue', marker='o'
)

ax.set_title('3D Plot of Fare, Trip Miles, and Dropoff Area')
ax.set_xlabel('Fare ($)')
ax.set_ylabel('Trip Miles')
ax.set_zlabel('Dropoff Area')

plt.show()