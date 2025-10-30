# Read the 1000 lines of taxi data from the taxi_1000.csv file
# Calculate total, average fare, and the maximum trip distance

import csv

with open('taxi_1000 - taxi_1000.csv', 'r') as file:
    csv_reader = csv.reader(file)

    total_fare = 0.0
    max_distance = 0.0
    average_fare = 0.0
    num_rows = 0

    for line in csv_reader:
        if num_rows == 0:
            # Skip header row
            num_rows += 1
            continue

        # Use the correct column indexes directly
        tripFare = float(line[10])       # fare_amount column
        distance = float(line[5])        # trip_distance column

        total_fare += tripFare
        if distance > max_distance:
            max_distance = distance

        num_rows += 1

    if num_rows > 1:
        average_fare = total_fare / (num_rows - 1)  # Exclude header row

    print(f"Total Fare: ${total_fare:.2f}")
    print(f"Average Fare: ${average_fare:.2f}")
    print(f"Maximum Trip Distance: {max_distance:.2f} miles")
