#Create a list of dictionaries from the given dictionary
trips = [{'miles': 1.1, 'fare': 6.25}, {'miles': 0.8, 'fare': 5.25},
            {'miles': 2.5, 'fare': 10.5}, {'miles': 2.6, 'fare': 8.05}     


                                                                ]
print(f"The fare of the third trip is ${trips[2]['fare']:.2f}")
price_by_miles = dict(zip(miles, fares))
print(price_by_miles)
print("3rd trip:", 2.5, "miles,", price_by_miles[2.5])