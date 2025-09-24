# create dictionary

trip_durations = [1.1, 0.8, 2.5, 2.6]
trip_fares= (6.25, 5.25, 10.5, 8.05)

trips = dict(zip(trip_durations, trip_fares))
print(trips)

trip_num = int(input("What trip do you want?:"))
print(f"Duration: {list(trips.keys())[trip_num-1]}miles")
print(f"Fare: ${list(trips.values())[trip_num-1]:.2f}")
#given this dictionary create a list of dictionaries, one per item where the first element is the key and second element is the value
trip_list = [1.1, 0.8, 2.5, 2.6]
fare_list = [6.25, 5.25, 10.5, 8.05]
trip_dicts = []
for i in range(len(trip_list)):
    trip_dicts.append({"miles": trip_list[i], "fare": fare_list[i]})
print(trip_dicts)
print(f"The fare of the third trip is ${trip_dicts[2]['fare']:.2f}")
print(f"The duration of the third trip is {trip_dicts[2]['miles']} miles")
#add a new trip of 2.2 miles and fare of $4.00
trip_dicts.append({"miles": 2.2, "fare": 4.00})
print(trip_dicts)