import pandas as pd
import matplotlib.pyplot as plt

trips_df = pd.read_json('Trips from area 8.json')

# Convert fare & trip_miles to numbers
trips_df['fare'] = pd.to_numeric(trips_df['fare'], errors='coerce')
trips_df['trip_miles'] = pd.to_numeric(trips_df['trip_miles'], errors='coerce')

# Drop rows with missing values
clean_df = trips_df.dropna(subset=['fare', 'trip_miles'])

# First scatter plot
plt.plot(clean_df['fare'], clean_df['trip_miles'],
         linestyle='none', marker='v', color='cyan', alpha=0.2)
plt.title('Fare vs Trip Miles (Fancy Style)')
plt.xlabel('Fare ($)')
plt.ylabel('Trip Miles')
plt.show()