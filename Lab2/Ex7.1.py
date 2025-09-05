def FtoC(degreesF, decimal_places):
    degreesF_float = float(degreesF)
    degreesC = (degreesF_float - 32) * 5/9
    degreesC = round(degreesC, decimal_places)
    return degreesC

degrees_F = input("Please enter a temperature in Fahrenheit: ")
decimal_places = int(input("How many decimal places do you want to round to? "))
degreesC = FtoC(degrees_F, decimal_places)

print(f"{degrees_F} degrees Fahrenheit is equivalent to {degreesC} degrees Celsius.")
