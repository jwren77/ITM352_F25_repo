#define a lsit of taxi trip durations in miles (with Values)
#use values 1.1, 0.8, 2.5, 2.6). Also define a tuple of fares for the same number of trips (use values “$6.25,” “$5.25,” “$10.50,” “$8.05”)Store both the tuple and the list as values in a dictionary called trips, with keys “miles” and “fares.
#store the tuple and list as values in a dictionary, with keys "miles" and "fares"
#name Joe Wren

trip_durations = [1.1, 0.8, 2.5, 2.6]
trip_fares = (6.25, 5.25, 10.50, 8.05)

trips = {
    "miles": trip_durations,
    "fares": trip_fares
}
print(trips)

print(f'The durations of the third trip is {trips["miles"][2]} miles')
print(f'The fare of the third trip is ${trips["fares"][2]:.2f}')

trips["miles"].append(2.2)
trips["fares"] += (4.00,)
print(trips)

trip_num = int(input('What trip do you want?: '))
print(f"Duration: {trips['miles'][trip_num - 1]} miles, Fare: ${trips['fares'][trip_num - 1]:.2f}")