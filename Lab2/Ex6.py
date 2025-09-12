#ask user their weight in pounds
#Convert to kg by dividing by 2.2046
#Print the result to the user rounded to 2 decimal places
#Name Joe Wren
#Date 9/5/2025

weight_in_pounds = input("Please enter your weight in pounds: ")
weight_in_kilos = float(weight_in_pounds) / 2.2046
rounded_kilos = round(weight_in_kilos, 0)
print(f"Your weight in kilos is {rounded_kilos} kg.")
print(f"Your weight in kilos is {round(float(input('Please enter your weight in pounds: ')) / 2.2046, 2)} kg.")
