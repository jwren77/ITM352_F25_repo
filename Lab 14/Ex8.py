import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the file
df = pd.read_csv('taxi trips Fri 7_7_2017.csv')

# Convert numeric columns (in case they are strings)
df['pickup_community_area'] = pd.to_numeric(df['pickup_community_area'], errors='coerce')
df['dropoff_community_area'] = pd.to_numeric(df['dropoff_community_area'], errors='coerce')

# Drop rows missing pickup or dropoff area
clean_df = df.dropna(subset=['pickup_community_area', 'dropoff_community_area'])

# Create a pivot table counting number of trips
heatmap_data = clean_df.pivot_table(
    index='pickup_community_area',
    columns='dropoff_community_area',
    aggfunc='size',
    fill_value=0
)

# Plot the heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(heatmap_data, cmap='viridis')
plt.title('Heatmap of Pickup vs Dropoff Community Areas')
plt.xlabel('Dropoff Community Area')
plt.ylabel('Pickup Community Area')

plt.show()