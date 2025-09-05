#ask the user to enter to enter a temperature in Fahrenheit temperature
#Convert to Celsius by subtracting 32 and divding by 5/9
#print a message to the user stating the tem in F they entered and equivalent in C
#Name Joe Wren
#Date 9/5/2025

degrees_f = input("Please enter a temperature in Fahrenheit: ")

degrees_f_float = float(degrees_f)
degrees_C = (degrees_f_float - 32) * 5/9
degrees_C = round(degrees_C)

print(f"{degrees_f_float} degrees Fahrenheit is equivalent to {degrees_C} degrees Celsius.")