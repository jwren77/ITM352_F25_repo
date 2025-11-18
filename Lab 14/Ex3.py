import pandas as pd
import matplotlib.pyplot as plt

trips_df = pd.read_json('Trips from area 8.json')

# Drop rows with NA in payment_type or tips
trips_df = trips_df.dropna(subset=['payment_type', 'tips'])

# Make sure tips is numeric
trips_df['tips'] = pd.to_numeric(trips_df['tips'], errors='coerce')
trips_df = trips_df.dropna(subset=['tips'])

# Sum tips by payment type
tip_totals = trips_df.groupby('payment_type')['tips'].sum()

plt.bar(tip_totals.index, tip_totals.values)
plt.title('Total Tips by Payment Method')
plt.xlabel('Payment Method')
plt.ylabel('Sum of Tips')

plt.xticks(rotation=45)
plt.show()